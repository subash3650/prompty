"""GuardRule model for dynamic difficulty configuration."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class GuardRule(Base):
    """
    Dynamic rule for input/output guards.
    Allows adjusting difficulty without code changes.
    """
    __tablename__ = "guard_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level_number = Column(Integer, ForeignKey("levels.level_number"), nullable=False)
    rule_type = Column(String(50), nullable=False)  # 'input' or 'output'
    rule_name = Column(String(100), nullable=False)
    rule_expression = Column(Text, nullable=False)  # Predicate logic or regex
    confidence_weight = Column(Float, default=1.0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    level = relationship("Level")
    
    __table_args__ = (
        UniqueConstraint('level_number', 'rule_name', name='uq_level_rule_name'),
    )

    def __repr__(self):
        return f"<GuardRule {self.rule_name} (Level {self.level_number})>"
