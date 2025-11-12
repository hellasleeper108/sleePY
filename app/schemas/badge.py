"""
Badge schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BadgeBase(BaseModel):
    """Base badge schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str
    icon: Optional[str] = None
    criteria: Optional[str] = None


class BadgeCreate(BadgeBase):
    """Schema for creating a new badge"""
    pass


class BadgeResponse(BadgeBase):
    """Schema for badge response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    """Schema for user badge (badge earned by user)"""
    id: int
    badge_id: int
    badge_name: str
    badge_description: str
    badge_icon: Optional[str] = None
    earned_at: datetime

    class Config:
        from_attributes = True
