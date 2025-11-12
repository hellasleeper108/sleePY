"""
User model - handles user accounts, authentication, and gamification
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class User(Base):
    """
    User model for PyQuest platform

    Tracks user account info, experience points, levels, and progress
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Profile fields
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Gamification fields
    xp = Column(Integer, default=0, index=True)  # Experience points (indexed for leaderboards)
    level = Column(Integer, default=1)  # Current level

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    loot_chests = relationship("LootChest", back_populates="user", cascade="all, delete-orphan")
    streak = relationship("DailyStreak", back_populates="user", uselist=False, cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("UserPathProgress", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', level={self.level}, xp={self.xp})>"

    def calculate_level(self):
        """
        Calculate user level based on XP
        Formula: level = floor(sqrt(xp / 100)) + 1

        Level thresholds:
        - Level 1: 0-99 XP
        - Level 2: 100-399 XP
        - Level 3: 400-899 XP
        - Level 4: 900-1599 XP
        - etc.
        """
        import math
        return math.floor(math.sqrt(self.xp / 100)) + 1

    def add_xp(self, amount: int):
        """
        Add XP to user and automatically level up if threshold is met

        Args:
            amount: Amount of XP to add

        Returns:
            bool: True if user leveled up, False otherwise
        """
        old_level = self.level
        self.xp += amount
        new_level = self.calculate_level()

        if new_level > old_level:
            self.level = new_level
            return True
        return False

    def xp_for_next_level(self):
        """
        Calculate XP needed for next level

        Returns:
            int: XP needed to reach next level
        """
        next_level_threshold = ((self.level) ** 2) * 100
        return next_level_threshold - self.xp
