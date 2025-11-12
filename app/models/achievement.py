"""
Achievement model - milestone-based auto-unlocking achievements
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum as SQLEnum
from datetime import datetime
import enum
from app.db.base import Base


class AchievementType(str, enum.Enum):
    """Types of achievement criteria"""
    CHALLENGE_COUNT = "challenge_count"     # Complete X challenges
    XP_TOTAL = "xp_total"                  # Reach X total XP
    LEVEL_REACHED = "level_reached"        # Reach level X
    STREAK_COUNT = "streak_count"          # Maintain X day streak
    CATEGORY_MASTER = "category_master"    # Complete all in a category
    PERFECT_SCORE = "perfect_score"        # Complete challenge on first try
    SPEED_RUN = "speed_run"                # Complete challenge quickly
    LOOT_COLLECTOR = "loot_collector"      # Open X loot chests


class Achievement(Base):
    """
    Achievement model for milestone-based rewards

    These are automatically checked and awarded based on user progress
    Unlike badges, achievements have specific unlock criteria
    """
    __tablename__ = "achievements"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Achievement details
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    icon = Column(String(50), nullable=True)  # Emoji or icon

    # Achievement type and criteria
    achievement_type = Column(SQLEnum(AchievementType), nullable=False)
    criteria_value = Column(Integer, nullable=False)  # Target value (e.g., 10 for "complete 10 challenges")
    category = Column(String(50), nullable=True)  # For category-specific achievements

    # Rewards
    xp_reward = Column(Integer, default=0)
    grants_loot_chest = Column(Boolean, default=False)

    # Display
    is_secret = Column(Boolean, default=False)  # Hidden until unlocked
    order = Column(Integer, default=0)

    def __repr__(self):
        return f"<Achievement(name='{self.name}', type='{self.achievement_type}', value={self.criteria_value})>"

    def check_unlock(self, user_stats: dict) -> bool:
        """
        Check if achievement should be unlocked based on user stats

        Args:
            user_stats: Dictionary with user statistics

        Returns:
            bool: True if criteria met
        """
        if self.achievement_type == AchievementType.CHALLENGE_COUNT:
            return user_stats.get("challenges_completed", 0) >= self.criteria_value

        elif self.achievement_type == AchievementType.XP_TOTAL:
            return user_stats.get("total_xp", 0) >= self.criteria_value

        elif self.achievement_type == AchievementType.LEVEL_REACHED:
            return user_stats.get("level", 0) >= self.criteria_value

        elif self.achievement_type == AchievementType.STREAK_COUNT:
            return user_stats.get("current_streak", 0) >= self.criteria_value

        elif self.achievement_type == AchievementType.CATEGORY_MASTER:
            category_progress = user_stats.get("category_completion", {})
            return category_progress.get(self.category, 0) >= 100  # 100% completion

        elif self.achievement_type == AchievementType.PERFECT_SCORE:
            return user_stats.get("perfect_scores", 0) >= self.criteria_value

        elif self.achievement_type == AchievementType.LOOT_COLLECTOR:
            return user_stats.get("chests_opened", 0) >= self.criteria_value

        return False

    def to_dict(self, unlocked: bool = False, progress: int = 0) -> dict:
        """
        Convert achievement to dictionary with progress

        Args:
            unlocked: Whether user has unlocked this
            progress: Current progress toward achievement

        Returns:
            dict: Achievement data with progress
        """
        return {
            "id": self.id,
            "name": self.name if not self.is_secret or unlocked else "???",
            "description": self.description if not self.is_secret or unlocked else "Secret Achievement",
            "icon": self.icon if not self.is_secret or unlocked else "🔒",
            "achievement_type": self.achievement_type.value,
            "criteria_value": self.criteria_value,
            "xp_reward": self.xp_reward,
            "unlocked": unlocked,
            "progress": progress,
            "progress_percentage": min(int((progress / self.criteria_value) * 100), 100) if self.criteria_value > 0 else 0
        }
