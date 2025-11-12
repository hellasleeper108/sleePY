"""
LearningPath model - structured learning courses for Python topics
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class PathDifficulty(str, enum.Enum):
    """Difficulty levels for learning paths"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PathTopic(str, enum.Enum):
    """Python topics for learning paths"""
    VARIABLES = "variables"
    CONTROL_FLOW = "control_flow"
    FUNCTIONS = "functions"
    DATA_STRUCTURES = "data_structures"
    OOP = "oop"
    MODULES = "modules"
    FILE_IO = "file_io"
    ERROR_HANDLING = "error_handling"
    COMPREHENSIONS = "comprehensions"
    DECORATORS = "decorators"


class LearningPath(Base):
    """
    LearningPath model for structured learning courses

    Each path covers a specific Python topic with lessons and challenges
    """
    __tablename__ = "learning_paths"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Path details
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    topic = Column(SQLEnum(PathTopic), nullable=False, index=True)
    difficulty = Column(SQLEnum(PathDifficulty), default=PathDifficulty.BEGINNER)

    # Learning info
    estimated_hours = Column(Integer, default=1)  # Estimated time to complete
    prerequisites = Column(Text, nullable=True)  # Comma-separated path IDs or descriptions

    # Gamification
    xp_reward = Column(Integer, default=100)  # XP for completing entire path
    required_level = Column(Integer, default=1)  # Minimum level to access
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=True)  # Badge awarded on completion

    # Metadata
    order = Column(Integer, default=0)  # Display order
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lessons = relationship("Lesson", back_populates="path", cascade="all, delete-orphan", order_by="Lesson.order")
    challenges = relationship("Challenge", back_populates="learning_path")
    user_progress = relationship("UserPathProgress", back_populates="path", cascade="all, delete-orphan")
    badge = relationship("Badge")

    def __repr__(self):
        return f"<LearningPath(title='{self.title}', topic='{self.topic}', difficulty='{self.difficulty}')>"

    def get_completion_requirements(self):
        """
        Get requirements to complete this path

        Returns:
            dict: Completion requirements
        """
        return {
            "lessons_required": len(self.lessons),
            "challenges_required": len(self.challenges),
            "xp_reward": self.xp_reward,
            "badge_id": self.badge_id
        }

    def get_progress_percentage(self, user_id: int, db) -> float:
        """
        Calculate user's progress percentage for this path

        Args:
            user_id: User ID
            db: Database session

        Returns:
            float: Progress percentage (0-100)
        """
        from app.models.user_lesson_progress import UserLessonProgress
        from app.models.progress import Progress

        total_items = len(self.lessons) + len(self.challenges)
        if total_items == 0:
            return 100.0

        # Count completed lessons
        completed_lessons = db.query(UserLessonProgress).filter(
            UserLessonProgress.user_id == user_id,
            UserLessonProgress.lesson_id.in_([l.id for l in self.lessons]),
            UserLessonProgress.is_completed == True
        ).count()

        # Count completed challenges
        completed_challenges = db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.challenge_id.in_([c.id for c in self.challenges]),
            Progress.is_completed == True
        ).count()

        completed = completed_lessons + completed_challenges
        return (completed / total_items) * 100
