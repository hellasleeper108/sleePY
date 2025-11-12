"""
Hint model - tracks AI mentor hints given to users
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Hint(Base):
    """
    Hint model tracks AI mentor interactions

    Records hints given to users for challenges
    Used to calculate bonus XP (fewer hints = more bonus)
    """
    __tablename__ = "hints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)

    # Hint content
    hint_text = Column(Text, nullable=False)
    hint_number = Column(Integer, nullable=False)  # 1st hint, 2nd hint, etc.

    # Context
    user_code = Column(Text, nullable=True)  # User's code when asking for hint
    error_message = Column(Text, nullable=True)  # Error if any

    # AI provider info
    ai_provider = Column(String(50), default="ollama")  # Which AI generated the hint

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="hints")
    challenge = relationship("Challenge", backref="hints")

    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_hint_user_challenge', 'user_id', 'challenge_id'),
        Index('idx_hint_created', 'created_at'),
    )

    def __repr__(self):
        return f"<Hint(user_id={self.user_id}, challenge_id={self.challenge_id}, hint_number={self.hint_number})>"

    @staticmethod
    def calculate_bonus_xp_multiplier(hint_count: int) -> float:
        """
        Calculate bonus XP multiplier based on number of hints used

        Args:
            hint_count: Number of hints requested

        Returns:
            float: Multiplier for bonus XP (1.0 = no bonus, 1.2 = +20%)
        """
        if hint_count == 0:
            return 1.2  # +20% bonus for solving without hints
        elif hint_count == 1:
            return 1.1  # +10% bonus for using only one hint
        elif hint_count == 2:
            return 1.05  # +5% bonus for using two hints
        else:
            return 1.0  # No bonus for 3+ hints
