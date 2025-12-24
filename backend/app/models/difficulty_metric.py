"""DifficultyMetric model for real-time analytics."""

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class DifficultyMetric(Base):
    """
    Snapshot of difficulty metrics for a level at a point in time.
    Used for calibration history and analytics.
    """
    __tablename__ = "difficulty_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level_number = Column(Integer, ForeignKey("levels.level_number"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Validation data
    attempts_last_hour = Column(Integer, default=0)
    successes_last_hour = Column(Integer, default=0)
    average_attempts_per_user = Column(Float)
    average_time_minutes = Column(Float)
    
    # Analysis
    prediction_confidence = Column(Float) # How confident we are in this assessment
    
    # Relationships
    level = relationship("Level")
    
    def __repr__(self):
        return f"<DifficultyMetric L{self.level_number} @ {self.timestamp}>"
