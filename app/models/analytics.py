"""
Analytics model for tracking user performance and engagement
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class UserActivity(Base):
    """
    Track user activity sessions for weekly active user calculations
    """
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # login, challenge_start, challenge_complete, etc.
    activity_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON string for additional data

    # Relationships
    user = relationship("User", back_populates="activities")

    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_user_activity_date', 'user_id', 'activity_date'),
        Index('idx_activity_type_date', 'activity_type', 'activity_date'),
    )


class ChallengeSession(Base):
    """
    Track individual challenge attempts with timing data
    """
    __tablename__ = "challenge_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Float, default=0.0)  # Total time in seconds
    is_completed = Column(Boolean, default=False)
    code_submitted = Column(Text, nullable=True)
    hints_used = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="challenge_sessions")
    challenge = relationship("Challenge", back_populates="sessions")

    # Indexes
    __table_args__ = (
        Index('idx_session_user_challenge', 'user_id', 'challenge_id'),
        Index('idx_session_started', 'started_at'),
        Index('idx_session_completed', 'is_completed', 'ended_at'),
    )

    def end_session(self, completed: bool = False):
        """Mark session as ended and calculate time spent"""
        self.ended_at = datetime.utcnow()
        if self.started_at:
            self.time_spent_seconds = (self.ended_at - self.started_at).total_seconds()
        self.is_completed = completed
