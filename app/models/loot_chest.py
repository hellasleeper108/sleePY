"""
LootChest model - random rewards for users
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class ChestRarity(str, enum.Enum):
    """Rarity levels for loot chests"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class LootChest(Base):
    """
    LootChest model for random rewards

    Chests are awarded to users for various activities and can be opened
    for random XP and bonus rewards
    """
    __tablename__ = "loot_chests"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Chest properties
    rarity = Column(SQLEnum(ChestRarity), default=ChestRarity.COMMON)
    xp_reward = Column(Integer, default=0)  # XP inside (set when opened)
    is_opened = Column(Boolean, default=False)

    # Metadata
    earned_reason = Column(String(200), nullable=True)  # Why user got this chest
    created_at = Column(DateTime, default=datetime.utcnow)
    opened_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="loot_chests")

    def __repr__(self):
        status = "opened" if self.is_opened else "unopened"
        return f"<LootChest(rarity='{self.rarity}', status='{status}', xp={self.xp_reward})>"

    @staticmethod
    def get_xp_range(rarity: ChestRarity) -> tuple[int, int]:
        """
        Get XP range for a chest rarity

        Args:
            rarity: Chest rarity level

        Returns:
            tuple: (min_xp, max_xp)
        """
        ranges = {
            ChestRarity.COMMON: (10, 30),
            ChestRarity.RARE: (30, 70),
            ChestRarity.EPIC: (70, 150),
            ChestRarity.LEGENDARY: (150, 300),
        }
        return ranges.get(rarity, (10, 30))

    @staticmethod
    def get_rarity_weights() -> dict:
        """
        Get probability weights for chest rarities

        Returns:
            dict: Rarity weights for random selection
        """
        return {
            ChestRarity.COMMON: 60,      # 60% chance
            ChestRarity.RARE: 25,        # 25% chance
            ChestRarity.EPIC: 12,        # 12% chance
            ChestRarity.LEGENDARY: 3,    # 3% chance
        }
