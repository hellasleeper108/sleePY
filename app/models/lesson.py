"""
Lesson model - individual lessons within learning paths
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class LessonType(str, enum.Enum):
    """Types of lessons"""
    TUTORIAL = "tutorial"          # Reading/learning content
    INTERACTIVE = "interactive"     # Code examples with explanations
    EXERCISE = "exercise"          # Practice exercises
    QUIZ = "quiz"                  # Knowledge check
    VIDEO = "video"                # Video lesson (future)


class Lesson(Base):
    """
    Lesson model for learning content

    Each lesson is part of a learning path and contains educational content
    """
    __tablename__ = "lessons"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False, index=True)

    # Lesson details
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Markdown content
    lesson_type = Column(SQLEnum(LessonType), default=LessonType.TUTORIAL)

    # Learning info
    order = Column(Integer, default=0)  # Order within the path
    estimated_minutes = Column(Integer, default=5)  # Estimated time
    xp_reward = Column(Integer, default=10)  # XP for completing lesson

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    path = relationship("LearningPath", back_populates="lessons")
    user_progress = relationship("UserLessonProgress", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lesson(title='{self.title}', type='{self.lesson_type}', path_id={self.path_id})>"

    def to_dict_preview(self):
        """
        Return lesson preview (without full content)

        Returns:
            dict: Lesson preview data
        """
        return {
            "id": self.id,
            "title": self.title,
            "lesson_type": self.lesson_type.value,
            "order": self.order,
            "estimated_minutes": self.estimated_minutes,
            "xp_reward": self.xp_reward
        }
