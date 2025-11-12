"""
UserPathProgress model - track user progress through learning paths
"""
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class UserPathProgress(Base):
    """
    UserPathProgress tracks user's progress through a learning path

    Records when user started, their current position, and completion status
    """
    __tablename__ = "user_path_progress"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False, index=True)

    # Progress tracking
    is_completed = Column(Boolean, default=False)
    current_lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)  # Last accessed lesson

    # XP tracking
    xp_earned = Column(Integer, default=0)  # Total XP earned from this path

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="learning_paths")
    path = relationship("LearningPath", back_populates="user_progress")
    current_lesson = relationship("Lesson", foreign_keys=[current_lesson_id])

    def __repr__(self):
        status = "completed" if self.is_completed else "in progress"
        return f"<UserPathProgress(user_id={self.user_id}, path_id={self.path_id}, status='{status}')>"

    def complete(self, xp_reward: int):
        """
        Mark path as completed

        Args:
            xp_reward: XP reward for completion
        """
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.xp_earned += xp_reward

    def update_position(self, lesson_id: int):
        """
        Update current lesson position

        Args:
            lesson_id: ID of lesson user is viewing
        """
        self.current_lesson_id = lesson_id
        self.last_accessed_at = datetime.utcnow()
