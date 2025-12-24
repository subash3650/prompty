"""User routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserProfile, UserStats
from app.security.jwt import get_current_user
from app.services.leaderboard_service import LeaderboardService
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's full profile.
    """
    leaderboard_service = LeaderboardService(db)
    rank_info = leaderboard_service.get_user_rank(current_user.id)
    
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        current_level=current_user.current_level,
        highest_level_reached=current_user.highest_level_reached,
        total_attempts=current_user.total_attempts,
        successful_attempts=current_user.successful_attempts,
        success_rate=current_user.success_rate,
        total_time_spent_seconds=current_user.total_time_spent_seconds,
        is_online=current_user.is_online,
        is_finished=current_user.is_finished,
        created_at=current_user.created_at,
        started_playing_at=current_user.started_playing_at,
        finished_at=current_user.finished_at,
        last_activity=current_user.last_activity,
        rank=rank_info.rank if rank_info else None,
    )


@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's quick stats.
    """
    leaderboard_service = LeaderboardService(db)
    rank_info = leaderboard_service.get_user_rank(current_user.id)
    
    return UserStats(
        current_level=current_user.current_level,
        highest_level_reached=current_user.highest_level_reached,
        total_attempts=current_user.total_attempts,
        successful_attempts=current_user.successful_attempts,
        success_rate=current_user.success_rate,
        rank=rank_info.rank if rank_info else None,
        total_players=rank_info.total_players if rank_info else None,
    )


@router.get("/{user_id}")
async def get_user_public_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get another user's public profile.
    
    Only returns non-sensitive information.
    """
    from fastapi import HTTPException, status
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    leaderboard_service = LeaderboardService(db)
    rank_info = leaderboard_service.get_user_rank(user_id)
    
    return {
        "id": user.id,
        "username": user.username,
        "highest_level_reached": user.highest_level_reached,
        "total_attempts": user.total_attempts,
        "successful_attempts": user.successful_attempts,
        "success_rate": user.success_rate,
        "is_finished": user.is_finished,
        "rank": rank_info.rank if rank_info else None,
    }
