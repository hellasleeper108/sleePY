"""
UserLessonProgress model - track user completion of individual lessons
"""
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class UserLessonProgress(Base):
    """
    UserLessonProgress tracks completion of individual lessons

    Records when lessons are completed and XP earned
    """
    __tablename__ = "user_lesson_progress"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)

    # Progress tracking
    is_completed = Column(Boolean, default=False)
    xp_earned = Column(Integer, default=0)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    lesson = relationship("Lesson", back_populates="user_progress")

    # Constraints - user can only complete each lesson once
    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),
    )

    def __repr__(self):
        status = "completed" if self.is_completed else "in progress"
        return f"<UserLessonProgress(user_id={self.user_id}, lesson_id={self.lesson_id}, status='{status}')>"

    def complete(self, xp_reward: int):
        """
        Mark lesson as completed

        Args:
            xp_reward: XP reward for completion
        """
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.xp_earned = xp_reward
