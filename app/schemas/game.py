"""
Game schemas for loot, streaks, and achievements
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from app.models.loot_chest import ChestRarity
from app.models.achievement import AchievementType


# Loot Chest Schemas
class LootChestResponse(BaseModel):
    """Schema for loot chest response"""
    id: int
    rarity: ChestRarity
    xp_reward: int
    is_opened: bool
    earned_reason: Optional[str] = None
    created_at: datetime
    opened_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OpenChestResult(BaseModel):
    """Schema for chest opening result"""
    chest_id: int
    rarity: str
    xp_reward: int
    xp_gained: int
    total_xp: int
    old_level: int
    new_level: int
    leveled_up: bool
    levels_gained: int


# Daily Streak Schemas
class StreakResponse(BaseModel):
    """Schema for streak information"""
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CheckInResult(BaseModel):
    """Schema for daily check-in result"""
    streak_continued: bool
    current_streak: int
    bonus_xp: int
    message: str
    streak_broken: Optional[bool] = None
    lost_streak: Optional[int] = None
    milestone_reward: Optional[dict] = None


# Achievement Schemas
class AchievementResponse(BaseModel):
    """Schema for achievement response"""
    id: int
    name: str
    description: str
    icon: Optional[str] = None
    achievement_type: AchievementType
    criteria_value: int
    xp_reward: int
    grants_loot_chest: bool
    is_secret: bool

    class Config:
        from_attributes = True


class AchievementProgressResponse(BaseModel):
    """Schema for achievement with user progress"""
    id: int
    name: str
    description: str
    icon: Optional[str] = None
    achievement_type: str
    criteria_value: int
    xp_reward: int
    unlocked: bool
    progress: int
    progress_percentage: int


class UserAchievementResponse(BaseModel):
    """Schema for unlocked achievement"""
    id: int
    achievement_id: int
    achievement_name: str
    achievement_description: str
    achievement_icon: Optional[str] = None
    unlocked_at: datetime

    class Config:
        from_attributes = True


# Game Stats Schemas
class GameStatsResponse(BaseModel):
    """Schema for comprehensive game statistics"""
    user_id: int
    username: str
    level: int
    xp: int
    xp_for_next_level: int
    challenges_completed: int
    perfect_scores: int
    current_streak: int
    longest_streak: int
    unopened_chests: int
    opened_chests: int
    achievements_unlocked: int
    total_achievements: int


class XPAwardResult(BaseModel):
    """Schema for XP award result"""
    xp_gained: int
    total_xp: int
    old_level: int
    new_level: int
    leveled_up: bool
    levels_gained: int
    level_up_chest: Optional[dict] = None
