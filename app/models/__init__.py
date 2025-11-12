"""
Database models for PyQuest
"""
from app.models.user import User
from app.models.challenge import Challenge
from app.models.progress import Progress
from app.models.badge import Badge, UserBadge
from app.models.loot_chest import LootChest, ChestRarity
from app.models.daily_streak import DailyStreak
from app.models.achievement import Achievement, AchievementType
from app.models.user_achievement import UserAchievement
from app.models.learning_path import LearningPath, PathDifficulty, PathTopic
from app.models.lesson import Lesson, LessonType
from app.models.user_path_progress import UserPathProgress
from app.models.user_lesson_progress import UserLessonProgress
from app.models.friendship import Friendship
from app.models.duel import Duel, DuelStatus
from app.models.hint import Hint
from app.models.analytics import UserActivity, ChallengeSession

__all__ = [
    "User", "Challenge", "Progress", "Badge", "UserBadge",
    "LootChest", "ChestRarity", "DailyStreak",
    "Achievement", "AchievementType", "UserAchievement",
    "LearningPath", "PathDifficulty", "PathTopic",
    "Lesson", "LessonType",
    "UserPathProgress", "UserLessonProgress",
    "Friendship", "Duel", "DuelStatus",
    "Hint",
    "UserActivity", "ChallengeSession"
]
