"""User-related Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    """Schema for user registration."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (alphanumeric + underscore)"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 chars)"
    )
    email: Optional[EmailStr] = Field(None, description="Optional email address")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric with underscores only")
        return v.lower()


class UserLogin(BaseModel):
    """Schema for user login."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    
    id: str
    username: str
    email: Optional[str] = None
    current_level: int
    highest_level_reached: int
    total_attempts: int
    successful_attempts: int
    success_rate: float
    is_online: bool
    is_finished: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Schema for user profile with detailed stats."""
    
    id: str
    username: str
    email: Optional[str] = None
    current_level: int
    highest_level_reached: int
    total_attempts: int
    successful_attempts: int
    success_rate: float
    total_time_spent_seconds: int
    is_online: bool
    is_finished: bool
    created_at: datetime
    started_playing_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    rank: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """Schema for quick user statistics."""
    
    current_level: int
    highest_level_reached: int
    total_attempts: int
    successful_attempts: int
    success_rate: float
    rank: Optional[int] = None
    total_players: Optional[int] = None
