"""Session model for JWT token management."""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class Session(Base):
    """
    Session model for tracking active JWT tokens.
    
    Enables:
    - Token revocation
    - Session tracking
    - Security monitoring
    """
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token details
    token_jti = Column(String(500), unique=True, nullable=False, index=True)  # JWT ID
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    browser_fingerprint = Column(String(256), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationship
    user = relationship("User", back_populates="sessions")
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.is_active and not self.is_expired and self.revoked_at is None
    
    def __repr__(self) -> str:
        status = "active" if self.is_valid else "invalid"
        return f"<Session {status} User:{self.user_id[:8]}>"
