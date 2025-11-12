"""
Analytics Service - Calculate user performance and engagement metrics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

from app.models.user import User
from app.models.challenge import Challenge, ChallengeCategory
from app.models.progress import Progress
from app.models.analytics import UserActivity, ChallengeSession
from app.models.hint import Hint


class AnalyticsService:
    """Service for calculating analytics and metrics"""

    @staticmethod
    def get_time_spent_per_challenge(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Calculate average time spent on each challenge

        Args:
            db: Database session
            limit: Maximum number of results

        Returns:
            List of challenge time statistics
        """
        results = db.query(
            Challenge.id,
            Challenge.title,
            Challenge.difficulty,
            Challenge.category,
            func.count(ChallengeSession.id).label('total_attempts'),
            func.avg(ChallengeSession.time_spent_seconds).label('avg_time_seconds'),
            func.min(ChallengeSession.time_spent_seconds).label('min_time_seconds'),
            func.max(ChallengeSession.time_spent_seconds).label('max_time_seconds'),
            func.sum(
                func.cast(ChallengeSession.is_completed, db.bind.dialect.name == 'postgresql' and 'INTEGER' or 'INTEGER')
            ).label('completed_count')
        ).join(
            ChallengeSession, Challenge.id == ChallengeSession.challenge_id
        ).filter(
            ChallengeSession.ended_at.isnot(None)
        ).group_by(
            Challenge.id, Challenge.title, Challenge.difficulty, Challenge.category
        ).order_by(
            desc('total_attempts')
        ).limit(limit).all()

        return [
            {
                'challenge_id': r.id,
                'title': r.title,
                'difficulty': r.difficulty.value,
                'category': r.category.value,
                'total_attempts': r.total_attempts,
                'avg_time_seconds': round(r.avg_time_seconds or 0, 2),
                'avg_time_minutes': round((r.avg_time_seconds or 0) / 60, 2),
                'min_time_minutes': round((r.min_time_seconds or 0) / 60, 2),
                'max_time_minutes': round((r.max_time_seconds or 0) / 60, 2),
                'completed_count': r.completed_count or 0,
                'completion_rate': round((r.completed_count or 0) / r.total_attempts * 100, 2) if r.total_attempts > 0 else 0
            }
            for r in results
        ]

    @staticmethod
    def get_completion_rates_by_topic(db: Session) -> List[Dict[str, Any]]:
        """
        Calculate completion rates for each challenge category/topic

        Args:
            db: Database session

        Returns:
            List of topic completion statistics
        """
        results = db.query(
            Challenge.category,
            func.count(Progress.id).label('total_attempts'),
            func.sum(
                func.cast(Progress.is_completed, db.bind.dialect.name == 'postgresql' and 'INTEGER' or 'INTEGER')
            ).label('completed_count'),
            func.count(func.distinct(Progress.user_id)).label('unique_users')
        ).join(
            Progress, Challenge.id == Progress.challenge_id
        ).group_by(
            Challenge.category
        ).order_by(
            Challenge.category
        ).all()

        return [
            {
                'topic': r.category.value,
                'total_attempts': r.total_attempts,
                'completed_count': r.completed_count or 0,
                'completion_rate': round((r.completed_count or 0) / r.total_attempts * 100, 2) if r.total_attempts > 0 else 0,
                'unique_users': r.unique_users
            }
            for r in results
        ]

    @staticmethod
    def get_weekly_active_users(db: Session, weeks: int = 4) -> List[Dict[str, Any]]:
        """
        Calculate weekly active users for the past N weeks

        Args:
            db: Database session
            weeks: Number of weeks to analyze

        Returns:
            List of weekly active user counts
        """
        results = []
        today = datetime.utcnow()

        for i in range(weeks):
            week_start = today - timedelta(weeks=i+1)
            week_end = today - timedelta(weeks=i)

            # Count distinct users with activity in this week
            active_count = db.query(
                func.count(func.distinct(UserActivity.user_id))
            ).filter(
                and_(
                    UserActivity.activity_date >= week_start,
                    UserActivity.activity_date < week_end
                )
            ).scalar() or 0

            # Count distinct users who completed challenges
            completed_challenges = db.query(
                func.count(func.distinct(Progress.user_id))
            ).filter(
                and_(
                    Progress.is_completed == True,
                    Progress.completed_at >= week_start,
                    Progress.completed_at < week_end
                )
            ).scalar() or 0

            results.append({
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'week_label': f"Week {i+1}",
                'active_users': active_count,
                'users_completed_challenges': completed_challenges
            })

        return list(reversed(results))  # Oldest to newest

    @staticmethod
    def get_xp_distribution(db: Session) -> Dict[str, Any]:
        """
        Calculate XP distribution statistics across all users

        Args:
            db: Database session

        Returns:
            XP distribution statistics
        """
        # Basic stats
        stats = db.query(
            func.count(User.id).label('total_users'),
            func.avg(User.xp).label('avg_xp'),
            func.min(User.xp).label('min_xp'),
            func.max(User.xp).label('max_xp'),
            func.sum(User.xp).label('total_xp')
        ).filter(User.is_active == True).first()

        # XP brackets
        brackets = [
            ('0-100', 0, 100),
            ('101-500', 101, 500),
            ('501-1000', 501, 1000),
            ('1001-2500', 1001, 2500),
            ('2501-5000', 2501, 5000),
            ('5001+', 5001, 999999999)
        ]

        distribution = []
        for label, min_xp, max_xp in brackets:
            count = db.query(func.count(User.id)).filter(
                and_(
                    User.is_active == True,
                    User.xp >= min_xp,
                    User.xp <= max_xp
                )
            ).scalar() or 0

            distribution.append({
                'bracket': label,
                'count': count,
                'percentage': round(count / stats.total_users * 100, 2) if stats.total_users > 0 else 0
            })

        return {
            'total_users': stats.total_users,
            'avg_xp': round(stats.avg_xp or 0, 2),
            'min_xp': stats.min_xp or 0,
            'max_xp': stats.max_xp or 0,
            'total_xp': stats.total_xp or 0,
            'distribution': distribution
        }

    @staticmethod
    def get_engagement_overview(db: Session) -> Dict[str, Any]:
        """
        Get overall engagement metrics

        Args:
            db: Database session

        Returns:
            Engagement overview statistics
        """
        today = datetime.utcnow()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Daily active users (last 24 hours)
        dau = db.query(
            func.count(func.distinct(UserActivity.user_id))
        ).filter(
            UserActivity.activity_date >= today - timedelta(days=1)
        ).scalar() or 0

        # Weekly active users
        wau = db.query(
            func.count(func.distinct(UserActivity.user_id))
        ).filter(
            UserActivity.activity_date >= week_ago
        ).scalar() or 0

        # Monthly active users
        mau = db.query(
            func.count(func.distinct(UserActivity.user_id))
        ).filter(
            UserActivity.activity_date >= month_ago
        ).scalar() or 0

        # Total challenges completed (all time)
        total_completed = db.query(
            func.count(Progress.id)
        ).filter(
            Progress.is_completed == True
        ).scalar() or 0

        # Challenges completed this week
        week_completed = db.query(
            func.count(Progress.id)
        ).filter(
            and_(
                Progress.is_completed == True,
                Progress.completed_at >= week_ago
            )
        ).scalar() or 0

        # Average hints per challenge
        avg_hints = db.query(
            func.avg(
                db.query(func.count(Hint.id))
                .filter(Hint.challenge_id == Progress.challenge_id)
                .filter(Hint.user_id == Progress.user_id)
                .correlate(Progress)
                .scalar_subquery()
            )
        ).filter(Progress.is_completed == True).scalar() or 0

        # Total active users
        total_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0

        return {
            'daily_active_users': dau,
            'weekly_active_users': wau,
            'monthly_active_users': mau,
            'total_active_users': total_users,
            'total_challenges_completed': total_completed,
            'challenges_completed_this_week': week_completed,
            'avg_hints_per_challenge': round(avg_hints, 2),
            'engagement_rate_weekly': round(wau / total_users * 100, 2) if total_users > 0 else 0
        }

    @staticmethod
    def log_activity(db: Session, user_id: int, activity_type: str, metadata: Dict[str, Any] = None):
        """
        Log a user activity for analytics tracking

        Args:
            db: Database session
            user_id: User ID
            activity_type: Type of activity (login, challenge_start, etc.)
            metadata: Additional data to store
        """
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_date=datetime.utcnow(),
            metadata=json.dumps(metadata) if metadata else None
        )
        db.add(activity)
        db.commit()

    @staticmethod
    def start_challenge_session(db: Session, user_id: int, challenge_id: int) -> ChallengeSession:
        """
        Start tracking a challenge session

        Args:
            db: Database session
            user_id: User ID
            challenge_id: Challenge ID

        Returns:
            Created ChallengeSession
        """
        session = ChallengeSession(
            user_id=user_id,
            challenge_id=challenge_id,
            started_at=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Also log activity
        AnalyticsService.log_activity(db, user_id, 'challenge_start', {'challenge_id': challenge_id})

        return session

    @staticmethod
    def end_challenge_session(db: Session, session_id: int, completed: bool = False, code: str = None, hints_used: int = 0):
        """
        End a challenge session and calculate time spent

        Args:
            db: Database session
            session_id: Session ID
            completed: Whether challenge was completed
            code: Code submitted
            hints_used: Number of hints used
        """
        session = db.query(ChallengeSession).filter(ChallengeSession.id == session_id).first()
        if session:
            session.end_session(completed)
            session.code_submitted = code
            session.hints_used = hints_used
            db.commit()

            # Log completion activity
            if completed:
                AnalyticsService.log_activity(
                    db,
                    session.user_id,
                    'challenge_complete',
                    {
                        'challenge_id': session.challenge_id,
                        'time_spent': session.time_spent_seconds,
                        'hints_used': hints_used
                    }
                )
