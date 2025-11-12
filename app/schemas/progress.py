"""
Progress schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProgressBase(BaseModel):
    """Base progress schema"""
    challenge_id: int


class ProgressCreate(ProgressBase):
    """Schema for starting a challenge"""
    pass


class ProgressUpdate(BaseModel):
    """Schema for updating progress"""
    submitted_code: Optional[str] = None
    is_completed: Optional[bool] = None


class SubmitCode(BaseModel):
    """Schema for submitting code for a challenge"""
    code: str = Field(..., min_length=1)
    challenge_id: int


class ProgressResponse(ProgressBase):
    """Schema for progress response"""
    id: int
    user_id: int
    is_completed: bool
    attempts: int
    xp_earned: int
    submitted_code: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_attempted_at: datetime

    class Config:
        from_attributes = True


class ProgressWithChallenge(ProgressResponse):
    """Schema for progress with challenge details"""
    challenge_title: str
    challenge_difficulty: str
    challenge_xp_reward: int


class SubmissionResult(BaseModel):
    """Schema for code submission result"""
    success: bool
    message: str
    xp_earned: int = 0
    leveled_up: bool = False
    new_level: Optional[int] = None
    attempts: int = 0
