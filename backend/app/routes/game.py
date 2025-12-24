"""Game routes - prompt submission and game status."""

from typing import Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.game import (
    PromptSubmission,
    PromptResponse,
    GameStatus,
    LevelInfo,
    AttemptResponse,
    AttemptHistoryResponse,
    PasswordSubmission,
    PasswordResponse,
)
from app.services.game_service import GameService
from app.security.jwt import get_current_user
from app.security.rate_limit import limiter, RATE_LIMIT_GAME
from app.models.user import User


router = APIRouter(prefix="/game", tags=["Game"])


@router.get("/status", response_model=GameStatus)
async def get_game_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's game status.
    
    Returns current level, stats, and level info.
    """
    game_service = GameService(db)
    return game_service.get_user_game_status(current_user)


@router.post("/submit-prompt", response_model=PromptResponse)
@limiter.limit(RATE_LIMIT_GAME)
async def submit_prompt(
    request: Request,
    submission: PromptSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a prompt to Gandalf.
    
    This is the main game endpoint. The prompt is:
    1. Validated
    2. Checked by input guards
    3. Sent to the AI (Groq)
    4. Checked by output guards
    5. Evaluated for success
    
    Rate limited to 10 prompts per minute.
    """
    game_service = GameService(db)
    return game_service.submit_prompt(current_user, submission)


@router.post("/submit-password", response_model=PasswordResponse)
async def submit_password(
    request: Request,
    submission: PasswordSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a password guess to advance to the next level.
    
    Users extract the password from Gandalf's response and submit it here.
    If correct, they advance to the next level.
    """
    try:
        game_service = GameService(db)
        return game_service.verify_password(
            current_user, 
            submission.password, 
            submission.level
        )
    except Exception as e:
        import traceback
        with open("password_error.txt", "w") as f:
            f.write(traceback.format_exc())
        raise e


@router.get("/levels/{level_number}", response_model=LevelInfo)
async def get_level_info(
    level_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about a specific level.
    
    Does not reveal the secret password.
    """
    from fastapi import HTTPException, status
    
    game_service = GameService(db)
    level = game_service.get_level(level_number)
    
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level {level_number} not found"
        )
    
    return LevelInfo(
        level_number=level.level_number,
        defense_description=level.defense_description,
        hint=level.hint,
        difficulty_rating=level.difficulty_rating,
        total_attempts_made=level.total_attempts_made,
        success_rate=float(level.success_rate or 0),
        input_guard_type=level.input_guard_type,
        output_guard_type=level.output_guard_type,
    )


@router.get("/attempts", response_model=AttemptHistoryResponse)
async def get_attempts(
    level: Optional[int] = Query(None, ge=1, le=8, description="Filter by level"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's attempt history.
    
    Supports pagination and optional level filtering.
    """
    game_service = GameService(db)
    offset = (page - 1) * per_page
    
    attempts, total = game_service.get_user_attempts(
        user_id=current_user.id,
        level_number=level,
        limit=per_page,
        offset=offset
    )
    
    return AttemptHistoryResponse(
        attempts=[
            AttemptResponse(
                id=a.id,
                level_number=a.level_number,
                user_prompt=a.user_prompt,
                ai_response=a.ai_response,
                was_successful=a.was_successful,
                input_guard_triggered=a.input_guard_triggered,
                output_guard_triggered=a.output_guard_triggered,
                ai_latency_ms=a.ai_latency_ms,
                submitted_at=a.submitted_at,
                attempt_number=a.attempt_number,
            )
            for a in attempts
        ],
        total=total,
        page=page,
        per_page=per_page,
        has_more=offset + len(attempts) < total,
    )
