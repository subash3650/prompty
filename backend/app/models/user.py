"""User model for participant data and progress tracking."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class User(Base):
    """
    User model representing a participant in the Prompty Challenge.
    
    Tracks:
    - Authentication credentials
    - Game progress (current level, highest level)
    - Statistics (attempts, success rate)
    - Timestamps for tiebreaker logic
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Progress tracking
    current_level = Column(Integer, default=1, nullable=False)
    highest_level_reached = Column(Integer, default=1, nullable=False)
    
    # Statistics
    total_attempts = Column(Integer, default=0, nullable=False)
    successful_attempts = Column(Integer, default=0, nullable=False)
    total_time_spent_seconds = Column(Integer, default=0, nullable=False)
    
    # Timestamps (critical for tiebreaker)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_playing_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status flags
    is_online = Column(Boolean, default=True, nullable=False)
    is_finished = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    attempts = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")
    level_completions = relationship("LevelCompletion", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("current_level >= 1 AND current_level <= 9", name="valid_current_level"),
        CheckConstraint("highest_level_reached >= 1", name="valid_highest_level"),
        CheckConstraint("successful_attempts <= total_attempts", name="valid_attempts"),
        CheckConstraint("highest_level_reached >= current_level", name="valid_progress"),
    )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful_attempts / self.total_attempts) * 100
    
    def __repr__(self) -> str:
        return f"<User {self.username} (Level {self.current_level})>"
