"""
Pydantic schemas for community features (friends, duels, leaderboards)
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.duel import DuelStatus
from app.models.challenge import ChallengeCategory


# ==================== FRIENDSHIP SCHEMAS ====================

class FriendshipCreate(BaseModel):
    """Schema for creating a friendship (following someone)"""
    following_id: int = Field(..., description="User ID to follow")


class FriendResponse(BaseModel):
    """Schema for friend information"""
    user_id: int
    username: str
    full_name: str
    xp: int
    level: int
    followed_at: datetime

    class Config:
        from_attributes = True


class FriendListResponse(BaseModel):
    """Schema for list of friends"""
    following: List[FriendResponse]  # People the user follows
    followers: List[FriendResponse]  # People who follow the user
    following_count: int
    follower_count: int


# ==================== DUEL SCHEMAS ====================

class DuelCreate(BaseModel):
    """Schema for creating a duel challenge"""
    opponent_id: int = Field(..., description="User ID of opponent")
    challenge_id: int = Field(..., description="Challenge ID for duel")
    xp_stake: int = Field(default=50, ge=10, le=500, description="XP stake (winner bonus)")


class DuelResponse(BaseModel):
    """Schema for duel information"""
    id: int
    challenge_id: int
    challenge_title: Optional[str] = None
    challenger_id: int
    challenger_username: Optional[str] = None
    opponent_id: int
    opponent_username: Optional[str] = None
    status: DuelStatus
    xp_stake: int
    created_at: datetime
    accepted_at: Optional[datetime] = None
    expires_at: datetime
    completed_at: Optional[datetime] = None
    winner_id: Optional[int] = None
    challenger_completion_time: Optional[float] = None
    opponent_completion_time: Optional[float] = None
    challenger_xp_earned: int = 0
    opponent_xp_earned: int = 0
    time_remaining_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class DuelAccept(BaseModel):
    """Schema for accepting a duel"""
    duel_id: int


class DuelSubmission(BaseModel):
    """Schema for submitting duel completion"""
    duel_id: int
    completion_time: float = Field(..., description="Time taken in seconds")
    code: str = Field(..., description="Code solution")


class DuelResult(BaseModel):
    """Schema for duel results"""
    duel_id: int
    status: DuelStatus
    winner_id: Optional[int] = None
    winner_username: Optional[str] = None
    challenger_time: Optional[float] = None
    opponent_time: Optional[float] = None
    challenger_xp: int
    opponent_xp: int
    message: str


# ==================== LEADERBOARD SCHEMAS ====================

class LeaderboardEntry(BaseModel):
    """Schema for a leaderboard entry"""
    rank: int
    user_id: int
    username: str
    full_name: str
    xp: int = Field(0, description="Total XP")
    level: int
    challenges_completed: int = 0

    class Config:
        from_attributes = True


class WeeklyLeaderboardEntry(LeaderboardEntry):
    """Schema for weekly leaderboard entry"""
    weekly_xp: int = Field(0, description="XP earned this week")
    total_xp: int = Field(0, description="Total all-time XP")


class TopicLeaderboardEntry(LeaderboardEntry):
    """Schema for topic-based leaderboard entry"""
    topic_xp: int = Field(0, description="XP earned in this topic")
    total_xp: int = Field(0, description="Total all-time XP")
    category: str


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response"""
    leaderboard_type: str = Field(..., description="Type of leaderboard (global, weekly, topic)")
    entries: List[LeaderboardEntry]
    total_count: int
    current_page: int = 1
    page_size: int = 100
    user_rank: Optional[int] = None


class UserRankResponse(BaseModel):
    """Schema for user's rank information"""
    user_id: int
    global_rank: Optional[int] = None
    weekly_rank: Optional[int] = None
    total_users: int


# ==================== SEARCH/FILTER SCHEMAS ====================

class UserSearchResponse(BaseModel):
    """Schema for user search results"""
    user_id: int
    username: str
    full_name: str
    xp: int
    level: int
    is_following: bool = False

    class Config:
        from_attributes = True
