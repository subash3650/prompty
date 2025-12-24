"""JWT token creation and verification."""

from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenData


settings = get_settings()
security = HTTPBearer()


def create_access_token(
    user_id: str,
    username: str,
    is_admin: bool = False,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, str, datetime]:
    """
    Create a JWT access token.
    
    Returns:
        Tuple of (token, jti, expiration_datetime)
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expire_hours)
    
    jti = str(uuid.uuid4())  # Unique token ID for revocation
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": user_id,
        "username": username,
        "is_admin": is_admin,
        "jti": jti,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt, jti, expire


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        is_admin: bool = payload.get("is_admin", False)
        jti: str = payload.get("jti")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(
            user_id=user_id,
            username=username,
            is_admin=is_admin,
            jti=jti
        )
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    
    Usage:
        @app.get("/me")
        def get_me(user: User = Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last activity
    user.last_activity = datetime.utcnow()
    user.is_online = True
    db.commit()
    
    return user


async def get_current_admin(
    user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current authenticated admin user.
    
    Usage:
        @app.get("/admin/stats")
        def get_stats(admin: User = Depends(get_current_admin)):
            return {"stats": ...}
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
