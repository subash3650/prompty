"""Leaderboard service - handles ranking calculations and tiebreaker logic."""

from datetime import datetime
from typing import List, Optional
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from app.models.user import User
from app.models.level_completion import LevelCompletion
from app.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse, RankResponse


logger = logging.getLogger(__name__)


class LeaderboardService:
    """Service for leaderboard ranking calculations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_leaderboard(
        self,
        current_user_id: Optional[str] = None,
        limit: int = 100
    ) -> LeaderboardResponse:
        """
        Get the full leaderboard with rankings.
        
        Ranking Algorithm:
        1. Sort by highest_level_reached (descending)
        2. For ties, sort by completion_time of that level (ascending - earlier is better)
        3. For remaining ties, sort by total successful_attempts (descending)
        """
        # Get max level reached by anyone
        max_level = self.db.query(func.max(User.highest_level_reached)).scalar() or 1
        
        # Query all users with their completion times for their highest level
        users_query = self.db.query(User).filter(
            User.is_admin == False  # Exclude admins from leaderboard
        ).all()
        
        # Build ranking data
        ranking_data = []
        for user in users_query:
            # Get completion time for user's highest level
            completion = self.db.query(LevelCompletion).filter(
                LevelCompletion.user_id == user.id,
                LevelCompletion.level_number == user.highest_level_reached
            ).first()
            
            completion_time = completion.completed_at if completion else None
            
            ranking_data.append({
                "user": user,
                "highest_level": user.highest_level_reached,
                "completion_time": completion_time,
                "successful_attempts": user.successful_attempts,
            })
        
        # Sort by: highest_level DESC, completion_time ASC, successful_attempts DESC
        def sort_key(item):
            level = item["highest_level"]
            # For completion_time, earlier is better (ascending)
            # Use a large date for None values to put them last
            ct = item["completion_time"]
            if ct is None:
                ct = datetime(9999, 12, 31)
            return (-level, ct, -item["successful_attempts"])
        
        ranking_data.sort(key=sort_key)
        
        # Build leaderboard entries with ranks
        entries = []
        your_rank = None
        
        for rank, data in enumerate(ranking_data[:limit], 1):
            user = data["user"]
            is_current = user.id == current_user_id
            
            if is_current:
                your_rank = rank
            
            entries.append(LeaderboardEntry(
                rank=rank,
                user_id=user.id,
                username=user.username,
                highest_level_reached=user.highest_level_reached,
                completion_time=data["completion_time"],
                total_attempts=user.total_attempts,
                successful_attempts=user.successful_attempts,
                success_rate=user.success_rate,
                is_current_user=is_current,
            ))
        
        return LeaderboardResponse(
            entries=entries,
            total_players=len(users_query),
            max_level_reached=max_level,
            your_rank=your_rank,
            last_updated=datetime.utcnow(),
        )
    
    def get_user_rank(self, user_id: str) -> Optional[RankResponse]:
        """Get a specific user's rank."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Count users ranked higher
        # Higher level OR same level with earlier completion
        completion = self.db.query(LevelCompletion).filter(
            LevelCompletion.user_id == user_id,
            LevelCompletion.level_number == user.highest_level_reached
        ).first()
        
        user_completion_time = completion.completed_at if completion else datetime(9999, 12, 31)
        
        # Count users ahead
        ahead_count = self.db.query(User).filter(
            User.is_admin == False,
            User.id != user_id
        ).filter(
            (User.highest_level_reached > user.highest_level_reached) |
            (
                (User.highest_level_reached == user.highest_level_reached) &
                (User.id.in_(
                    self.db.query(LevelCompletion.user_id).filter(
                        LevelCompletion.level_number == user.highest_level_reached,
                        LevelCompletion.completed_at < user_completion_time
                    )
                ))
            )
        ).count()
        
        rank = ahead_count + 1
        total = self.db.query(User).filter(User.is_admin == False).count()
        
        return RankResponse(
            user_id=user.id,
            username=user.username,
            rank=rank,
            highest_level_reached=user.highest_level_reached,
            completion_time=completion.completed_at if completion else None,
            total_players=total,
        )
    
    def get_winners(self, top_n: int = 3) -> List[LeaderboardEntry]:
        """Get the top N winners."""
        leaderboard = self.get_leaderboard(limit=top_n)
        return leaderboard.entries[:top_n]
