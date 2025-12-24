"""Authentication-related Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    
    user_id: Optional[str] = None
    username: Optional[str] = None
    is_admin: bool = False
    jti: Optional[str] = None  # JWT ID for revocation


class LoginResponse(BaseModel):
    """Schema for login response with user data."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    current_level: int
    is_admin: bool = False


class RefreshRequest(BaseModel):
    """Schema for token refresh request."""
    
    refresh_token: str
