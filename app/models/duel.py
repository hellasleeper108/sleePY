"""
Duel model - handles 1v1 challenge competitions
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum as SQLEnum, Float, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Optional
import enum
from app.db.base import Base


class DuelStatus(str, enum.Enum):
    """Status of a duel"""
    PENDING = "pending"  # Waiting for opponent to accept
    ACTIVE = "active"  # Both users accepted, in progress
    COMPLETED = "completed"  # Duel finished
    CANCELLED = "cancelled"  # Duel cancelled
    EXPIRED = "expired"  # Duel expired (not accepted in time)


class Duel(Base):
    """
    Duel model for 1v1 challenge competitions

    Two users compete on the same challenge
    Fastest correct solution wins bonus XP
    """
    __tablename__ = "duels"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    challenger_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    opponent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    status = Column(SQLEnum(DuelStatus), default=DuelStatus.PENDING, nullable=False, index=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)  # Auto-expires if not accepted
    completed_at = Column(DateTime, nullable=True)

    # Results
    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    challenger_completion_time = Column(Float, nullable=True)  # Time in seconds
    opponent_completion_time = Column(Float, nullable=True)  # Time in seconds
    challenger_xp_earned = Column(Integer, default=0)
    opponent_xp_earned = Column(Integer, default=0)

    # Stakes
    xp_stake = Column(Integer, default=50, nullable=False)  # Bonus XP for winner

    # Relationships
    challenge = relationship("Challenge", backref="duels")
    challenger = relationship("User", foreign_keys=[challenger_id], backref="duels_initiated")
    opponent = relationship("User", foreign_keys=[opponent_id], backref="duels_received")
    winner = relationship("User", foreign_keys=[winner_id], backref="duels_won")

    # Indexes
    __table_args__ = (
        Index('idx_duel_challenger', 'challenger_id', 'status'),
        Index('idx_duel_opponent', 'opponent_id', 'status'),
        Index('idx_duel_active', 'status', 'created_at'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Default expiration: 24 hours
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)

    def accept(self) -> bool:
        """Accept the duel"""
        if self.status != DuelStatus.PENDING:
            return False
        if datetime.utcnow() > self.expires_at:
            self.status = DuelStatus.EXPIRED
            return False
        self.status = DuelStatus.ACTIVE
        self.accepted_at = datetime.utcnow()
        return True

    def submit_completion(self, user_id: int, completion_time: float) -> bool:
        """
        Record completion time for a user

        Args:
            user_id: ID of user who completed
            completion_time: Time taken in seconds

        Returns:
            bool: True if this submission resulted in duel completion
        """
        if self.status != DuelStatus.ACTIVE:
            return False

        if user_id == self.challenger_id:
            self.challenger_completion_time = completion_time
        elif user_id == self.opponent_id:
            self.opponent_completion_time = completion_time
        else:
            return False

        # Check if both have completed
        if self.challenger_completion_time and self.opponent_completion_time:
            self._determine_winner()
            return True

        return False

    def _determine_winner(self):
        """Determine the winner based on completion times"""
        if not self.challenger_completion_time or not self.opponent_completion_time:
            return

        challenger_time = self.challenger_completion_time
        opponent_time = self.opponent_completion_time

        # Faster completion wins
        if challenger_time < opponent_time:
            self.winner_id = self.challenger_id
            self.challenger_xp_earned = self.xp_stake
            self.opponent_xp_earned = self.xp_stake // 2  # Loser gets half
        elif opponent_time < challenger_time:
            self.winner_id = self.opponent_id
            self.opponent_xp_earned = self.xp_stake
            self.challenger_xp_earned = self.xp_stake // 2
        else:
            # Tie - both get half
            self.challenger_xp_earned = self.xp_stake // 2
            self.opponent_xp_earned = self.xp_stake // 2

        self.status = DuelStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def cancel(self) -> bool:
        """Cancel the duel"""
        if self.status in [DuelStatus.PENDING, DuelStatus.ACTIVE]:
            self.status = DuelStatus.CANCELLED
            return True
        return False

    def get_time_remaining(self) -> Optional[timedelta]:
        """Get time remaining before expiration"""
        if self.status != DuelStatus.PENDING:
            return None
        remaining = self.expires_at - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def __repr__(self):
        return f"<Duel {self.id} ({self.challenger_id} vs {self.opponent_id}) - {self.status}>"
