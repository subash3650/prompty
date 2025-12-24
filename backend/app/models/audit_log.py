"""AuditLog model for security and compliance logging."""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
import uuid

from app.models.base import Base


class AuditLog(Base):
    """
    AuditLog model for tracking security-relevant events.
    
    Records:
    - Login attempts
    - Prompt submissions
    - Guard triggering
    - Suspicious activity
    - Admin actions
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event classification
    event_type = Column(String(100), nullable=False, index=True)
    # Examples: 'login', 'logout', 'prompt_submitted', 'level_passed',
    #           'guard_triggered', 'suspicious_activity', 'password_exposure_attempt'
    
    # Associated user (nullable for system events)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Event details (flexible JSON)
    details = Column(JSON, nullable=True)
    
    # Severity classification
    severity = Column(String(20), default="info")  # 'info', 'warning', 'critical'
    
    # Security indicators
    suspicious_flag = Column(Boolean, default=False, index=True)
    cheating_detected = Column(Boolean, default=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Source tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog {self.event_type} at {self.created_at}>"
