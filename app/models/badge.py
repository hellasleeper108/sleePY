"""
Badge models - handles achievements and badges
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Badge(Base):
    """
    Badge model for achievements

    Defines available badges that users can earn
    """
    __tablename__ = "badges"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Badge details
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    icon = Column(String(50), nullable=True)  # Emoji or icon identifier

    # Badge criteria (for documentation/display)
    criteria = Column(Text, nullable=True)  # Description of how to earn

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Badge(name='{self.name}', icon='{self.icon}')>"


class UserBadge(Base):
    """
    UserBadge model for tracking which badges users have earned

    Junction table between User and Badge with earning timestamp
    """
    __tablename__ = "user_badges"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, index=True)

    # Metadata
    earned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")

    # Constraints - user can only earn each badge once
    __table_args__ = (
        UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),
    )

    def __repr__(self):
        return f"<UserBadge(user_id={self.user_id}, badge_id={self.badge_id})>"
