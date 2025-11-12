"""
Progress model - tracks user completion of challenges
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Progress(Base):
    """
    Progress model tracks which challenges users have completed

    Records user submissions, completion status, and earned XP
    """
    __tablename__ = "progress"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False, index=True)

    # Progress tracking
    is_completed = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)  # Number of submission attempts
    xp_earned = Column(Integer, default=0)  # XP earned from this challenge

    # User's code submission
    submitted_code = Column(Text, nullable=True)  # User's latest submission

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress")
    challenge = relationship("Challenge", back_populates="progress")

    # Indexes for optimized queries
    __table_args__ = (
        Index('idx_progress_completed', 'is_completed', 'completed_at'),
        Index('idx_progress_weekly', 'user_id', 'is_completed', 'completed_at'),
    )

    def __repr__(self):
        status = "completed" if self.is_completed else "in progress"
        return f"<Progress(user_id={self.user_id}, challenge_id={self.challenge_id}, status='{status}')>"

    def complete(self, xp_reward: int):
        """
        Mark challenge as completed and record XP

        Args:
            xp_reward: Amount of XP to award
        """
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.xp_earned = xp_reward

    def record_attempt(self, code: str):
        """
        Record a new attempt at the challenge

        Args:
            code: User's submitted code
        """
        self.attempts += 1
        self.submitted_code = code
        self.last_attempted_at = datetime.utcnow()
