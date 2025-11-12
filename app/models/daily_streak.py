"""
DailyStreak model - track user activity streaks
"""
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.db.base import Base


class DailyStreak(Base):
    """
    DailyStreak model tracks consecutive days of user activity

    Streaks are maintained by daily check-ins or completing challenges
    """
    __tablename__ = "daily_streaks"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key (one-to-one with User)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Streak tracking
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)  # Last day user was active

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="streak")

    def __repr__(self):
        return f"<DailyStreak(user_id={self.user_id}, current={self.current_streak}, longest={self.longest_streak})>"

    def check_in(self, activity_date: date = None) -> dict:
        """
        Record a check-in for the user

        Args:
            activity_date: Date of activity (defaults to today)

        Returns:
            dict: Result with streak info and rewards
        """
        if activity_date is None:
            activity_date = date.today()

        # First check-in ever
        if self.last_activity_date is None:
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = activity_date
            return {
                "streak_continued": True,
                "current_streak": self.current_streak,
                "bonus_xp": 0,
                "message": "Streak started! Come back tomorrow to keep it going."
            }

        # Calculate days since last activity
        days_diff = (activity_date - self.last_activity_date).days

        # Same day - no change
        if days_diff == 0:
            return {
                "streak_continued": False,
                "current_streak": self.current_streak,
                "bonus_xp": 0,
                "message": "You've already checked in today!"
            }

        # Consecutive day - extend streak
        elif days_diff == 1:
            self.current_streak += 1
            self.last_activity_date = activity_date

            # Update longest streak if needed
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak

            # Calculate bonus XP (5 XP per streak day, max 50)
            bonus_xp = min(self.current_streak * 5, 50)

            return {
                "streak_continued": True,
                "current_streak": self.current_streak,
                "bonus_xp": bonus_xp,
                "message": f"🔥 {self.current_streak} day streak! +{bonus_xp} bonus XP!"
            }

        # Streak broken
        else:
            old_streak = self.current_streak
            self.current_streak = 1
            self.last_activity_date = activity_date

            return {
                "streak_continued": False,
                "current_streak": self.current_streak,
                "bonus_xp": 0,
                "message": f"Streak broken! You had {old_streak} days. Starting fresh!",
                "streak_broken": True,
                "lost_streak": old_streak
            }

    def get_milestone_rewards(self) -> list[int]:
        """
        Get list of streak milestones that award special rewards

        Returns:
            list: Streak day numbers that award bonuses
        """
        return [3, 7, 14, 30, 60, 100, 365]

    def is_milestone(self, streak_day: int = None) -> bool:
        """
        Check if current streak is at a milestone

        Args:
            streak_day: Streak day to check (defaults to current)

        Returns:
            bool: True if at milestone
        """
        if streak_day is None:
            streak_day = self.current_streak

        return streak_day in self.get_milestone_rewards()
