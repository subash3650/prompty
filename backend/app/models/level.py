"""Level model for game level definitions with defenses."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Numeric, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class Level(Base):
    """
    Level model representing a game level with its defenses.
    
    Each level has:
    - A secret password to protect
    - System prompt instructions for the AI
    - Input and output guard configurations
    - Statistics on player performance
    """
    
    __tablename__ = "levels"
    
    # Primary key
    id = Column(Integer, primary_key=True)
    level_number = Column(Integer, unique=True, nullable=False, index=True)
    
    # Secrets and prompts
    secret_password = Column(String(100), nullable=False)
    password_variations = Column(Text, nullable=True)  # JSON array of variations
    system_prompt = Column(Text, nullable=False)
    
    # Defense mechanisms
    input_guard_type = Column(String(50), nullable=False, default="none")
    # Options: 'none', 'lexical', 'semantic', 'intent', 'classifier', 'combined', 'adaptive'
    
    output_guard_type = Column(String(50), nullable=False, default="none")
    # Options: 'none', 'exact_match', 'semantic', 'combined', 'adaptive'
    
    # Metadata
    defense_description = Column(Text, nullable=False)
    hint = Column(Text, nullable=True)
    difficulty_rating = Column(Integer, default=1)  # 1-5 stars

    # Difficulty Scaling Engine
    difficulty_base_score = Column(Numeric(4, 1))
    measured_difficulty_score = Column(Numeric(4, 1))
    
    input_guard_confidence_threshold = Column(Numeric(3, 2), default=0.5)
    output_guard_confidence_threshold = Column(Numeric(3, 2), default=0.5)
    
    success_rate_target = Column(Numeric(5, 2), default=50.0)
    average_attempts_target = Column(Integer, default=5)
    time_to_pass_target_minutes = Column(Integer, default=5)
    
    difficulty_last_calibrated = Column(DateTime)
    calibration_count = Column(Integer, default=0)
    
    discovered_bypass_techniques = Column(Text)
    password_variations_count = Column(Integer, default=0)
    
    start_hint = Column(Text)
    
    # Real-time statistics
    total_attempts_made = Column(Integer, default=0)
    successful_attempts_made = Column(Integer, default=0)
    success_rate = Column(Numeric(5, 2), default=0.0)
    average_attempts_to_pass = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempts = relationship("Attempt", back_populates="level")
    completions = relationship("LevelCompletion", back_populates="level")
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage."""
        if self.total_attempts_made == 0:
            return 0.0
        return float(self.successful_attempts_made / self.total_attempts_made * 100)
    
    def __repr__(self) -> str:
        return f"<Level {self.level_number}: {self.defense_description[:30]}...>"
