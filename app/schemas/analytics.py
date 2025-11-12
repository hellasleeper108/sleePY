"""
Analytics schemas for API responses
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChallengeTimeStats(BaseModel):
    """Statistics for time spent on a challenge"""
    challenge_id: int
    title: str
    difficulty: str
    category: str
    total_attempts: int
    avg_time_seconds: float
    avg_time_minutes: float
    min_time_minutes: float
    max_time_minutes: float
    completed_count: int
    completion_rate: float


class TopicCompletionStats(BaseModel):
    """Completion statistics for a topic/category"""
    topic: str
    total_attempts: int
    completed_count: int
    completion_rate: float
    unique_users: int


class WeeklyActiveUsers(BaseModel):
    """Weekly active user statistics"""
    week_start: str
    week_end: str
    week_label: str
    active_users: int
    users_completed_challenges: int


class XPBracket(BaseModel):
    """XP distribution bracket"""
    bracket: str
    count: int
    percentage: float


class XPDistribution(BaseModel):
    """XP distribution across users"""
    total_users: int
    avg_xp: float
    min_xp: int
    max_xp: int
    total_xp: int
    distribution: List[XPBracket]


class EngagementOverview(BaseModel):
    """Overall engagement metrics"""
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    total_active_users: int
    total_challenges_completed: int
    challenges_completed_this_week: int
    avg_hints_per_challenge: float
    engagement_rate_weekly: float


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard data"""
    engagement: EngagementOverview
    time_per_challenge: List[ChallengeTimeStats]
    completion_by_topic: List[TopicCompletionStats]
    weekly_active: List[WeeklyActiveUsers]
    xp_distribution: XPDistribution


class SessionStart(BaseModel):
    """Request to start a challenge session"""
    challenge_id: int


class SessionEnd(BaseModel):
    """Request to end a challenge session"""
    session_id: int
    completed: bool = False
    code: Optional[str] = None
    hints_used: int = 0


class SessionResponse(BaseModel):
    """Challenge session response"""
    id: int
    user_id: int
    challenge_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    time_spent_seconds: float
    is_completed: bool
    hints_used: int

    class Config:
        from_attributes = True
