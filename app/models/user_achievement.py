"""
UserAchievement model - track unlocked achievements per user
"""
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class UserAchievement(Base):
    """
    UserAchievement model tracks which achievements users have unlocked

    Junction table between User and Achievement
    """
    __tablename__ = "user_achievements"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False, index=True)

    # Metadata
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)  # Whether user has been notified

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")

    # Constraints - user can only unlock each achievement once
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"
