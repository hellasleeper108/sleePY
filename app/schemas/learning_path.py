"""
Learning path schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.learning_path import PathDifficulty, PathTopic
from app.models.lesson import LessonType


# Lesson Schemas
class LessonBase(BaseModel):
    """Base lesson schema"""
    title: str = Field(..., min_length=3, max_length=200)
    content: str
    lesson_type: LessonType = LessonType.TUTORIAL
    order: int = Field(default=0, ge=0)
    estimated_minutes: int = Field(default=5, ge=1)
    xp_reward: int = Field(default=10, ge=1)


class LessonCreate(LessonBase):
    """Schema for creating a lesson"""
    path_id: int


class LessonResponse(LessonBase):
    """Schema for lesson response"""
    id: int
    path_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LessonPreview(BaseModel):
    """Schema for lesson preview (without full content)"""
    id: int
    title: str
    lesson_type: LessonType
    order: int
    estimated_minutes: int
    xp_reward: int


# Learning Path Schemas
class LearningPathBase(BaseModel):
    """Base learning path schema"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    topic: PathTopic
    difficulty: PathDifficulty = PathDifficulty.BEGINNER
    estimated_hours: int = Field(default=1, ge=1)
    prerequisites: Optional[str] = None
    xp_reward: int = Field(default=100, ge=1)
    required_level: int = Field(default=1, ge=1)
    badge_id: Optional[int] = None
    order: int = Field(default=0, ge=0)


class LearningPathCreate(LearningPathBase):
    """Schema for creating a learning path"""
    pass


class LearningPathUpdate(BaseModel):
    """Schema for updating a learning path"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    topic: Optional[PathTopic] = None
    difficulty: Optional[PathDifficulty] = None
    estimated_hours: Optional[int] = Field(None, ge=1)
    prerequisites: Optional[str] = None
    xp_reward: Optional[int] = Field(None, ge=1)
    required_level: Optional[int] = Field(None, ge=1)
    badge_id: Optional[int] = None
    order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class LearningPathResponse(LearningPathBase):
    """Schema for learning path response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningPathWithLessons(LearningPathResponse):
    """Schema for learning path with lessons"""
    lessons: List[LessonPreview]
    challenge_count: int


class LearningPathDetail(LearningPathResponse):
    """Schema for detailed learning path (with full content)"""
    lessons: List[LessonResponse]
    challenge_ids: List[int]


# Progress Schemas
class PathProgressResponse(BaseModel):
    """Schema for user path progress"""
    id: int
    path_id: int
    path_title: str
    path_topic: str
    path_difficulty: str
    is_completed: bool
    progress_percentage: float
    current_lesson_id: Optional[int] = None
    xp_earned: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed_at: datetime


class LessonProgressResponse(BaseModel):
    """Schema for user lesson progress"""
    id: int
    lesson_id: int
    is_completed: bool
    xp_earned: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompleteLessonResult(BaseModel):
    """Schema for lesson completion result"""
    lesson_id: int
    xp_earned: int
    total_xp: int
    leveled_up: bool
    new_level: Optional[int] = None
    path_completed: bool = False
    path_completion_reward: Optional[dict] = None


class PathCompletionResult(BaseModel):
    """Schema for path completion result"""
    path_id: int
    path_title: str
    xp_earned: int
    badge_awarded: Optional[dict] = None
    total_xp: int
    leveled_up: bool
    new_level: Optional[int] = None
    achievements_unlocked: Optional[List[dict]] = None
