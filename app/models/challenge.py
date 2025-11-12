"""
Challenge model - handles coding challenges/quests
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class DifficultyLevel(str, enum.Enum):
    """Difficulty levels for challenges"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ChallengeCategory(str, enum.Enum):
    """Categories for organizing challenges"""
    BASICS = "basics"
    DATA_STRUCTURES = "data_structures"
    ALGORITHMS = "algorithms"
    OOP = "oop"
    FUNCTIONAL = "functional"
    WEB = "web"
    DATA_SCIENCE = "data_science"
    OTHER = "other"


class Challenge(Base):
    """
    Challenge model for coding exercises

    Each challenge represents a Python coding task that users can complete
    """
    __tablename__ = "challenges"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Challenge details
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)

    # Difficulty and categorization
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    category = Column(SQLEnum(ChallengeCategory), default=ChallengeCategory.BASICS)

    # Challenge content
    starter_code = Column(Text, nullable=True)  # Initial code provided to user
    solution = Column(Text, nullable=True)  # Sample solution (admin only)
    test_cases = Column(Text, nullable=True)  # JSON string of test cases

    # Gamification
    xp_reward = Column(Integer, default=10)  # XP awarded on completion
    required_level = Column(Integer, default=1)  # Minimum level to access

    # Learning path link (optional)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=True, index=True)

    # Metadata
    order = Column(Integer, default=0)  # For ordering challenges in a sequence
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress = relationship("Progress", back_populates="challenge", cascade="all, delete-orphan")
    learning_path = relationship("LearningPath", back_populates="challenges")
    sessions = relationship("ChallengeSession", back_populates="challenge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Challenge(title='{self.title}', difficulty='{self.difficulty}', xp={self.xp_reward})>"

    def to_dict_public(self):
        """
        Return challenge data without sensitive info (like solution)

        Returns:
            dict: Public challenge data
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instructions": self.instructions,
            "difficulty": self.difficulty.value,
            "category": self.category.value,
            "starter_code": self.starter_code,
            "xp_reward": self.xp_reward,
            "required_level": self.required_level,
            "order": self.order,
        }
