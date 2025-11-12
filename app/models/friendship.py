"""
Friendship model - handles user relationships (following system)
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Friendship(Base):
    """
    Friendship model for following users

    Represents a one-way follow relationship (similar to Twitter)
    User A follows User B does not mean User B follows User A
    """
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], backref="following_relationships")
    following = relationship("User", foreign_keys=[following_id], backref="follower_relationships")

    # Constraints
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_friendship'),
        Index('idx_follower', 'follower_id'),
        Index('idx_following', 'following_id'),
        Index('idx_active_friendships', 'follower_id', 'following_id', 'is_active'),
    )

    def __repr__(self):
        return f"<Friendship {self.follower_id} -> {self.following_id}>"
