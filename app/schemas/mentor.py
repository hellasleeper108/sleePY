"""
Pydantic schemas for Mentor AI
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HintRequest(BaseModel):
    """Request for a hint"""
    challenge_id: int = Field(..., description="Challenge ID")
    user_code: Optional[str] = Field(None, description="User's current code")
    error_message: Optional[str] = Field(None, description="Error message if any")


class HintResponse(BaseModel):
    """Response with hint"""
    hint_id: int
    hint_text: str
    hint_number: int
    total_hints: int
    bonus_multiplier: float
    bonus_percentage: int
    message: str

    class Config:
        from_attributes = True


class HintHistory(BaseModel):
    """Individual hint in history"""
    hint_number: int
    created_at: str
    had_code: bool
    had_error: bool


class HintStatistics(BaseModel):
    """Statistics about hints for a challenge"""
    total_hints: int
    bonus_multiplier: float
    bonus_percentage: int
    can_still_get_bonus: bool
    hints_used: List[HintHistory]


class ProviderStatus(BaseModel):
    """AI provider status"""
    provider_name: str
    is_available: bool
    is_active: bool


class MentorConfig(BaseModel):
    """Mentor configuration"""
    current_provider: str
    available_providers: List[ProviderStatus]
    bonus_xp_enabled: bool = True
