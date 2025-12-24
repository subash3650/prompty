"""Authentication service - handles user registration, login, and token management."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.session import Session as UserSession
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import LoginResponse
from app.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(
        self,
        user_data: UserCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[User, str]:
        """
        Register a new user.
        
        Args:
            user_data: Registration data (username, password, email)
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (User, access_token)
            
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username exists
        existing_user = self.db.query(User).filter(
            User.username == user_data.username.lower()
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists (if provided)
        if user_data.email:
            existing_email = self.db.query(User).filter(
                User.email == user_data.email
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        user = User(
            username=user_data.username.lower(),
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            ip_address=ip_address,
            user_agent=user_agent,
            started_playing_at=datetime.utcnow(),
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create access token
        token, jti, expires_at = create_access_token(
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin
        )
        
        # Create session record
        session = UserSession(
            user_id=user.id,
            token_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        self.db.add(session)
        self.db.commit()
        
        logger.info(f"New user registered: {user.username}")
        
        return user, token
    
    def login_user(
        self,
        credentials: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginResponse:
        """
        Authenticate a user and return access token.
        
        Args:
            credentials: Login credentials (username, password)
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            LoginResponse with token and user info
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user
        user = self.db.query(User).filter(
            User.username == credentials.username.lower()
        ).first()
        
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update user status
        user.is_online = True
        user.last_activity = datetime.utcnow()
        user.ip_address = ip_address
        user.user_agent = user_agent
        
        # Create access token
        token, jti, expires_at = create_access_token(
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin
        )
        
        # Create session record
        session = UserSession(
            user_id=user.id,
            token_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        self.db.add(session)
        self.db.commit()
        
        logger.info(f"User logged in: {user.username}")
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.jwt_expire_hours * 3600,
            user_id=user.id,
            username=user.username,
            current_level=user.current_level,
            is_admin=user.is_admin
        )
    
    def logout_user(self, user: User, jti: Optional[str] = None) -> bool:
        """
        Logout a user by invalidating their session.
        
        Args:
            user: The user to logout
            jti: JWT ID to specifically revoke
            
        Returns:
            True if logout was successful
        """
        user.is_online = False
        
        if jti:
            # Revoke specific session
            session = self.db.query(UserSession).filter(
                UserSession.token_jti == jti
            ).first()
            if session:
                session.is_active = False
                session.revoked_at = datetime.utcnow()
        else:
            # Revoke all active sessions
            self.db.query(UserSession).filter(
                UserSession.user_id == user.id,
                UserSession.is_active == True
            ).update({
                "is_active": False,
                "revoked_at": datetime.utcnow()
            })
        
        self.db.commit()
        logger.info(f"User logged out: {user.username}")
        
        return True
    
    def create_admin(self, username: str, password: str) -> User:
        """Create an admin user (for initial setup)."""
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            # Update to admin
            existing.is_admin = True
            existing.password_hash = hash_password(password)
            self.db.commit()
            return existing
        
        admin = User(
            username=username,
            password_hash=hash_password(password),
            is_admin=True
        )
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        
        logger.info(f"Admin user created: {username}")
        return admin
