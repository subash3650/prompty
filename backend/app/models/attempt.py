"""Attempt model for tracking individual prompt submissions."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class Attempt(Base):
    """
    Attempt model representing a single prompt submission.
    
    This is the core audit trail for the game, tracking:
    - The prompt submitted
    - The AI response
    - Guard triggering
    - Success/failure
    - Timing and tokens
    """
    
    __tablename__ = "attempts"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    level_number = Column(Integer, ForeignKey("levels.level_number"), nullable=False, index=True)
    
    # Prompt details
    user_prompt = Column(Text, nullable=False)
    prompt_length = Column(Integer, nullable=False)
    prompt_hash = Column(String(64), nullable=True)  # SHA-256 for deduplication
    
    # AI response details
    ai_response = Column(Text, nullable=False)
    response_length = Column(Integer, nullable=True)
    ai_latency_ms = Column(Integer, nullable=True)
    
    # Token usage tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    
    # Input guard results
    input_guard_triggered = Column(Boolean, default=False)
    input_guard_reason = Column(String(500), nullable=True)
    input_guard_confidence = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    
    # Output guard results
    output_guard_triggered = Column(Boolean, default=False)
    output_guard_reason = Column(String(500), nullable=True)
    output_guard_confidence = Column(Numeric(3, 2), nullable=True)
    
    # Result
    was_successful = Column(Boolean, default=False, index=True)
    attempt_number = Column(Integer, nullable=False)  # Nth attempt on this level
    
    # Timestamps (microsecond precision for accuracy)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ai_response_received_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Analytics
    time_since_last_attempt_ms = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="attempts")
    level = relationship("Level", back_populates="attempts")
    
    def __repr__(self) -> str:
        status = "✓" if self.was_successful else "✗"
        return f"<Attempt {status} User:{self.user_id[:8]} Level:{self.level_number}>"
