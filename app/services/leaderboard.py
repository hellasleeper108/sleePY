"""
Leaderboard service - optimized leaderboard queries with caching

Provides global, weekly, and topic-based leaderboards
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.user import User
from app.models.progress import Progress
from app.models.challenge import Challenge, ChallengeCategory
import time


class LeaderboardCache:
    """
    Simple in-memory cache for leaderboard data
    In production, use Redis or similar
    """
    def __init__(self, ttl: int = 300):  # 5 minutes default TTL
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set cache value with current timestamp"""
        self.cache[key] = (value, time.time())

    def invalidate(self, key: str):
        """Invalidate specific cache key"""
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Clear all cache"""
        self.cache.clear()


# Global cache instance
_cache = LeaderboardCache(ttl=300)  # 5 minutes


class LeaderboardService:
    """Service for generating and caching leaderboards"""

    @staticmethod
    def get_global_leaderboard(db: Session, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get global leaderboard based on total XP

        Optimized query with index on xp column
        Cached for 5 minutes

        Args:
            db: Database session
            limit: Number of users to return
            offset: Offset for pagination

        Returns:
            list: Leaderboard entries with rank, user info, and stats
        """
        cache_key = f"global_leaderboard_{limit}_{offset}"
        cached = _cache.get(cache_key)
        if cached:
            return cached

        # Optimized query using index on xp
        users = (
            db.query(User)
            .filter(User.is_active == True)
            .order_by(desc(User.xp), desc(User.id))  # Secondary sort by id for stability
            .limit(limit)
            .offset(offset)
            .all()
        )

        # Get challenge completion counts in bulk
        user_ids = [u.id for u in users]
        completion_counts = dict(
            db.query(Progress.user_id, func.count(Progress.id))
            .filter(
                Progress.user_id.in_(user_ids),
                Progress.is_completed == True
            )
            .group_by(Progress.user_id)
            .all()
        )

        leaderboard = []
        for rank, user in enumerate(users, start=offset + 1):
            leaderboard.append({
                'rank': rank,
                'user_id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'xp': user.xp,
                'level': user.level,
                'challenges_completed': completion_counts.get(user.id, 0),
            })

        _cache.set(cache_key, leaderboard)
        return leaderboard

    @staticmethod
    def get_weekly_leaderboard(db: Session, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get weekly leaderboard based on XP earned in the last 7 days

        Uses Progress table to track weekly XP
        Cached for 5 minutes

        Args:
            db: Database session
            limit: Number of users to return
            offset: Offset for pagination

        Returns:
            list: Weekly leaderboard entries
        """
        cache_key = f"weekly_leaderboard_{limit}_{offset}"
        cached = _cache.get(cache_key)
        if cached:
            return cached

        # Calculate XP earned in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)

        # Optimized query using index on completed_at
        weekly_xp = (
            db.query(
                Progress.user_id,
                func.sum(Progress.xp_earned).label('weekly_xp'),
                func.count(Progress.id).label('challenges_completed')
            )
            .filter(
                Progress.is_completed == True,
                Progress.completed_at >= week_ago
            )
            .group_by(Progress.user_id)
            .order_by(desc('weekly_xp'))
            .limit(limit)
            .offset(offset)
            .all()
        )

        # Get user info in bulk
        user_ids = [entry.user_id for entry in weekly_xp]
        users_dict = {
            u.id: u for u in
            db.query(User).filter(User.id.in_(user_ids)).all()
        } if user_ids else {}

        leaderboard = []
        for rank, entry in enumerate(weekly_xp, start=offset + 1):
            user = users_dict.get(entry.user_id)
            if user:
                leaderboard.append({
                    'rank': rank,
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'weekly_xp': int(entry.weekly_xp or 0),
                    'total_xp': user.xp,
                    'level': user.level,
                    'challenges_completed': entry.challenges_completed,
                })

        _cache.set(cache_key, leaderboard)
        return leaderboard

    @staticmethod
    def get_topic_leaderboard(
        db: Session,
        category: ChallengeCategory,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get topic-based leaderboard for specific challenge category

        Uses join between Progress and Challenge tables
        Cached for 5 minutes

        Args:
            db: Database session
            category: Challenge category
            limit: Number of users to return
            offset: Offset for pagination

        Returns:
            list: Topic-based leaderboard entries
        """
        cache_key = f"topic_leaderboard_{category}_{limit}_{offset}"
        cached = _cache.get(cache_key)
        if cached:
            return cached

        # Optimized query using indexes
        topic_stats = (
            db.query(
                Progress.user_id,
                func.sum(Progress.xp_earned).label('topic_xp'),
                func.count(Progress.id).label('challenges_completed')
            )
            .join(Challenge, Progress.challenge_id == Challenge.id)
            .filter(
                Progress.is_completed == True,
                Challenge.category == category
            )
            .group_by(Progress.user_id)
            .order_by(desc('topic_xp'))
            .limit(limit)
            .offset(offset)
            .all()
        )

        # Get user info in bulk
        user_ids = [entry.user_id for entry in topic_stats]
        users_dict = {
            u.id: u for u in
            db.query(User).filter(User.id.in_(user_ids)).all()
        } if user_ids else {}

        leaderboard = []
        for rank, entry in enumerate(topic_stats, start=offset + 1):
            user = users_dict.get(entry.user_id)
            if user:
                leaderboard.append({
                    'rank': rank,
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'topic_xp': int(entry.topic_xp or 0),
                    'total_xp': user.xp,
                    'level': user.level,
                    'challenges_completed': entry.challenges_completed,
                    'category': category.value,
                })

        _cache.set(cache_key, leaderboard)
        return leaderboard

    @staticmethod
    def get_user_rank(db: Session, user_id: int, leaderboard_type: str = 'global') -> Optional[int]:
        """
        Get user's rank in specified leaderboard

        Args:
            db: Database session
            user_id: User ID
            leaderboard_type: Type of leaderboard ('global', 'weekly')

        Returns:
            int: User's rank (1-indexed) or None if not ranked
        """
        if leaderboard_type == 'global':
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            # Count users with higher XP
            rank = (
                db.query(func.count(User.id))
                .filter(
                    User.is_active == True,
                    User.xp > user.xp
                )
                .scalar()
            )
            return rank + 1

        elif leaderboard_type == 'weekly':
            week_ago = datetime.utcnow() - timedelta(days=7)

            # Get user's weekly XP
            user_weekly_xp = (
                db.query(func.sum(Progress.xp_earned))
                .filter(
                    Progress.user_id == user_id,
                    Progress.is_completed == True,
                    Progress.completed_at >= week_ago
                )
                .scalar() or 0
            )

            # Count users with higher weekly XP
            rank = (
                db.query(func.count(func.distinct(Progress.user_id)))
                .filter(
                    Progress.is_completed == True,
                    Progress.completed_at >= week_ago
                )
                .group_by(Progress.user_id)
                .having(func.sum(Progress.xp_earned) > user_weekly_xp)
                .count()
            )
            return rank + 1

        return None

    @staticmethod
    def invalidate_cache(leaderboard_type: Optional[str] = None):
        """
        Invalidate leaderboard cache

        Args:
            leaderboard_type: Specific type to invalidate or None for all
        """
        if leaderboard_type:
            # Invalidate specific type (all variations)
            keys_to_delete = [k for k in _cache.cache.keys() if k.startswith(f"{leaderboard_type}_")]
            for key in keys_to_delete:
                _cache.invalidate(key)
        else:
            _cache.clear()

    @staticmethod
    def get_friends_leaderboard(db: Session, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Get leaderboard of user's friends

        Args:
            db: Database session
            user_id: User ID
            limit: Number of friends to return

        Returns:
            list: Friends leaderboard
        """
        from app.models.friendship import Friendship

        cache_key = f"friends_leaderboard_{user_id}_{limit}"
        cached = _cache.get(cache_key)
        if cached:
            return cached

        # Get user's friends (people they follow)
        friend_ids = (
            db.query(Friendship.following_id)
            .filter(
                Friendship.follower_id == user_id,
                Friendship.is_active == True
            )
            .all()
        )
        friend_ids = [f[0] for f in friend_ids]

        if not friend_ids:
            return []

        # Get friends' stats
        friends = (
            db.query(User)
            .filter(User.id.in_(friend_ids))
            .order_by(desc(User.xp))
            .limit(limit)
            .all()
        )

        # Get challenge completion counts
        completion_counts = dict(
            db.query(Progress.user_id, func.count(Progress.id))
            .filter(
                Progress.user_id.in_(friend_ids),
                Progress.is_completed == True
            )
            .group_by(Progress.user_id)
            .all()
        )

        leaderboard = []
        for rank, friend in enumerate(friends, start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': friend.id,
                'username': friend.username,
                'full_name': friend.full_name,
                'xp': friend.xp,
                'level': friend.level,
                'challenges_completed': completion_counts.get(friend.id, 0),
            })

        _cache.set(cache_key, leaderboard)
        return leaderboard
