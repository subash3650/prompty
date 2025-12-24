"""LevelCompletion model for precise tracking of level completions."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class LevelCompletion(Base):
    """
    LevelCompletion model for tracking when each user completes each level.
    
    This is critical for the tiebreaker logic:
    - The winner is whoever reached the highest level first
    - Timestamp precision is microseconds for fair ranking
    """
    
    __tablename__ = "level_completions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    level_number = Column(Integer, ForeignKey("levels.level_number"), nullable=False, index=True)
    
    # Completion details
    attempt_id = Column(String(36), ForeignKey("attempts.id"), nullable=False)
    completed_at = Column(DateTime, nullable=False, index=True)  # Critical for tiebreaker
    time_to_complete_seconds = Column(Integer, nullable=True)  # Time spent on this level
    attempts_needed = Column(Integer, nullable=False)  # Number of attempts to pass
    
    # Relationships
    user = relationship("User", back_populates="level_completions")
    level = relationship("Level", back_populates="completions")
    
    # Unique constraint: each user completes each level at most once
    __table_args__ = (
        UniqueConstraint("user_id", "level_number", name="unique_user_level_completion"),
    )
    
    def __repr__(self) -> str:
        return f"<LevelCompletion User:{self.user_id[:8]} Level:{self.level_number} at {self.completed_at}>"
