"""Authentication routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import LoginResponse, Token
from app.services.auth_service import AuthService
from app.security.jwt import get_current_user
from app.security.rate_limit import limiter, RATE_LIMIT_AUTH
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=LoginResponse)
@limiter.limit(RATE_LIMIT_AUTH)
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Returns access token on successful registration.
    """
    auth_service = AuthService(db)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    user, token = auth_service.register_user(
        user_data=user_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    from app.config import get_settings
    settings = get_settings()
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_hours * 3600,
        user_id=user.id,
        username=user.username,
        current_level=user.current_level,
        is_admin=user.is_admin
    )


@router.post("/login", response_model=LoginResponse)
@limiter.limit(RATE_LIMIT_AUTH)
async def login(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with username and password.
    
    Returns access token on successful login.
    """
    auth_service = AuthService(db)
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return auth_service.login_user(
        credentials=credentials,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout the current user.
    
    Invalidates the current session.
    """
    auth_service = AuthService(db)
    auth_service.logout_user(current_user)
    
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user info.
    
    Requires authentication.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "current_level": current_user.current_level,
        "highest_level_reached": current_user.highest_level_reached,
        "total_attempts": current_user.total_attempts,
        "successful_attempts": current_user.successful_attempts,
        "success_rate": current_user.success_rate,
        "is_admin": current_user.is_admin,
        "is_finished": current_user.is_finished,
        "created_at": current_user.created_at,
    }
