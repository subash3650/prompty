"""Game-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PromptSubmission(BaseModel):
    """Schema for prompt submission request."""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The prompt to submit to Prompty"
    )
    level: int = Field(
        ...,
        ge=1,
        le=8,
        description="Current level (1-8)"
    )


class PromptResponse(BaseModel):
    """Schema for prompt submission response."""
    
    success: bool = Field(..., description="Whether the level was passed")
    response: str = Field(..., description="AI response (may be filtered)")
    reason: Optional[str] = Field(None, description="Reason for guard triggering")
    current_level: int = Field(..., description="User's current level after attempt")
    ai_latency_ms: Optional[int] = Field(None, description="AI response time in ms")
    message: str = Field(..., description="Human-readable result message")
    attempt_number: Optional[int] = Field(None, description="Which attempt this was")
    input_guard_triggered: bool = Field(False, description="Whether input guard blocked")
    output_guard_triggered: bool = Field(False, description="Whether output guard blocked")


class GameStatus(BaseModel):
    """Schema for user's current game status."""
    
    user_id: str
    username: str
    current_level: int
    highest_level_reached: int
    total_attempts: int
    successful_attempts: int
    success_rate: float
    is_finished: bool
    level_info: Optional["LevelInfo"] = None
    rank: Optional[int] = None


class LevelInfo(BaseModel):
    """Schema for level information (without secrets)."""
    
    level_number: int
    defense_description: str
    hint: Optional[str] = None
    difficulty_rating: int
    total_attempts_made: int
    success_rate: float
    input_guard_type: str
    output_guard_type: str


class AttemptResponse(BaseModel):
    """Schema for individual attempt history."""
    
    id: str
    level_number: int
    user_prompt: str
    ai_response: str
    was_successful: bool
    input_guard_triggered: bool
    output_guard_triggered: bool
    ai_latency_ms: Optional[int] = None
    submitted_at: datetime
    attempt_number: int
    
    class Config:
        from_attributes = True


class AttemptHistoryResponse(BaseModel):
    """Schema for paginated attempt history."""
    
    attempts: List[AttemptResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


class PasswordSubmission(BaseModel):
    """Schema for password submission request."""
    
    password: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The password the user thinks they extracted"
    )
    level: int = Field(
        ...,
        ge=1,
        le=8,
        description="Current level (1-8)"
    )


class PasswordResponse(BaseModel):
    """Schema for password submission response."""
    
    success: bool = Field(..., description="Whether the password was correct")
    message: str = Field(..., description="Human-readable result message")
    current_level: int = Field(..., description="User's current level after attempt")
    is_finished: bool = Field(False, description="Whether user completed all levels")


# Update forward reference
GameStatus.model_rebuild()
