"""
Challenge schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.challenge import DifficultyLevel, ChallengeCategory


class ChallengeBase(BaseModel):
    """Base challenge schema"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    instructions: str
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    category: ChallengeCategory = ChallengeCategory.BASICS
    starter_code: Optional[str] = None
    test_cases: Optional[str] = None
    xp_reward: int = Field(default=10, ge=1)
    required_level: int = Field(default=1, ge=1)
    order: int = Field(default=0, ge=0)


class ChallengeCreate(ChallengeBase):
    """Schema for creating a new challenge"""
    solution: Optional[str] = None  # Admin only


class ChallengeUpdate(BaseModel):
    """Schema for updating a challenge"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    category: Optional[ChallengeCategory] = None
    starter_code: Optional[str] = None
    solution: Optional[str] = None
    test_cases: Optional[str] = None
    xp_reward: Optional[int] = Field(None, ge=1)
    required_level: Optional[int] = Field(None, ge=1)
    order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ChallengeResponse(ChallengeBase):
    """Schema for challenge response (without solution)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChallengeAdminResponse(ChallengeResponse):
    """Schema for challenge response with solution (admin only)"""
    solution: Optional[str] = None


class ChallengeListResponse(BaseModel):
    """Schema for paginated challenge list"""
    challenges: list[ChallengeResponse]
    total: int
    page: int
    page_size: int
