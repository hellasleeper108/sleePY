"""
Pydantic schemas for request/response validation
"""
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    Token,
    TokenData
)
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeListResponse
)
from app.schemas.progress import (
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
    SubmitCode
)
from app.schemas.badge import (
    BadgeCreate,
    BadgeResponse,
    UserBadgeResponse
)
from app.schemas.game import (
    LootChestResponse,
    OpenChestResult,
    StreakResponse,
    CheckInResult,
    AchievementResponse,
    AchievementProgressResponse,
    UserAchievementResponse,
    GameStatsResponse,
    XPAwardResult
)

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "UserUpdate", "Token", "TokenData",
    "ChallengeCreate", "ChallengeUpdate", "ChallengeResponse", "ChallengeListResponse",
    "ProgressCreate", "ProgressUpdate", "ProgressResponse", "SubmitCode",
    "BadgeCreate", "BadgeResponse", "UserBadgeResponse",
    "LootChestResponse", "OpenChestResult", "StreakResponse", "CheckInResult",
    "AchievementResponse", "AchievementProgressResponse", "UserAchievementResponse",
    "GameStatsResponse", "XPAwardResult"
]
