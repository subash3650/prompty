"""Leaderboard-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LeaderboardEntry(BaseModel):
    """Schema for a single leaderboard entry."""
    
    rank: int = Field(..., description="Current rank (1 = first place)")
    user_id: str
    username: str
    highest_level_reached: int
    completion_time: Optional[datetime] = Field(
        None,
        description="When they completed their highest level (for tiebreaker)"
    )
    total_attempts: int
    successful_attempts: int
    success_rate: float
    is_current_user: bool = Field(False, description="Whether this is the requesting user")
    
    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Schema for full leaderboard response."""
    
    entries: List[LeaderboardEntry]
    total_players: int
    max_level_reached: int = Field(..., description="Highest level reached by any player")
    your_rank: Optional[int] = Field(None, description="Requesting user's rank")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class RankResponse(BaseModel):
    """Schema for individual user rank lookup."""
    
    user_id: str
    username: str
    rank: int
    highest_level_reached: int
    completion_time: Optional[datetime] = None
    total_players: int
