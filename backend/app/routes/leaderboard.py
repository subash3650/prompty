"""Leaderboard routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.leaderboard import LeaderboardResponse, RankResponse
from app.services.leaderboard_service import LeaderboardService
from app.security.jwt import get_current_user
from app.models.user import User


router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(100, ge=1, le=200, description="Max entries to return"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the full leaderboard.
    
    Rankings are based on:
    1. Highest level reached (higher is better)
    2. Completion time for that level (earlier is better)
    3. Number of successful attempts (higher is better)
    
    Includes the current user's rank if authenticated.
    """
    leaderboard_service = LeaderboardService(db)
    
    return leaderboard_service.get_leaderboard(
        current_user_id=current_user.id if current_user else None,
        limit=limit
    )


@router.get("/rank/{user_id}", response_model=RankResponse)
async def get_user_rank(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific user's rank.
    """
    from fastapi import HTTPException, status
    
    leaderboard_service = LeaderboardService(db)
    rank = leaderboard_service.get_user_rank(user_id)
    
    if not rank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return rank


@router.get("/my-rank", response_model=RankResponse)
async def get_my_rank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's rank.
    """
    leaderboard_service = LeaderboardService(db)
    return leaderboard_service.get_user_rank(current_user.id)
