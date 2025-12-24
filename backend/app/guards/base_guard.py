"""Base guard interface and result model."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class GuardResult:
    """Result from a guard check."""
    
    blocked: bool
    reason: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    guard_type: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Allow using GuardResult in if statements."""
        return self.blocked


class BaseGuard(ABC):
    """Abstract base class for all guards."""
    
    guard_type: str = "base"
    
    @abstractmethod
    def check(self, content: str, **kwargs) -> GuardResult:
        """
        Check content against this guard.
        
        Args:
            content: The content to check (prompt or response)
            **kwargs: Additional context (level, secret, etc.)
            
        Returns:
            GuardResult with blocked status and reason
        """
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
