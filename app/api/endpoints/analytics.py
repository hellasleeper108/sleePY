"""
Analytics endpoints - admin dashboard metrics and user session tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.analytics import AnalyticsService
from app.schemas.analytics import (
    AnalyticsDashboard,
    EngagementOverview,
    ChallengeTimeStats,
    TopicCompletionStats,
    WeeklyActiveUsers,
    XPDistribution,
    SessionStart,
    SessionEnd,
    SessionResponse
)


router = APIRouter()


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify user is an admin

    Args:
        current_user: Current authenticated user

    Returns:
        User: Verified admin user

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/dashboard", response_model=AnalyticsDashboard)
def get_analytics_dashboard(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get complete analytics dashboard data (admin only)

    Returns comprehensive metrics including:
    - Engagement overview (DAU, WAU, MAU)
    - Time spent per challenge
    - Completion rates by topic
    - Weekly active users trend
    - XP distribution

    Args:
        admin: Verified admin user
        db: Database session

    Returns:
        AnalyticsDashboard: Complete dashboard data
    """
    engagement = AnalyticsService.get_engagement_overview(db)
    time_stats = AnalyticsService.get_time_spent_per_challenge(db, limit=20)
    completion_stats = AnalyticsService.get_completion_rates_by_topic(db)
    weekly_active = AnalyticsService.get_weekly_active_users(db, weeks=8)
    xp_dist = AnalyticsService.get_xp_distribution(db)

    return AnalyticsDashboard(
        engagement=engagement,
        time_per_challenge=time_stats,
        completion_by_topic=completion_stats,
        weekly_active=weekly_active,
        xp_distribution=xp_dist
    )


@router.get("/engagement", response_model=EngagementOverview)
def get_engagement_metrics(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get engagement overview metrics (admin only)

    Args:
        admin: Verified admin user
        db: Database session

    Returns:
        EngagementOverview: Engagement statistics
    """
    return AnalyticsService.get_engagement_overview(db)


@router.get("/time-per-challenge", response_model=list[ChallengeTimeStats])
def get_challenge_time_stats(
    limit: int = 50,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get time spent statistics per challenge (admin only)

    Args:
        limit: Maximum number of challenges to return
        admin: Verified admin user
        db: Database session

    Returns:
        List[ChallengeTimeStats]: Time statistics for each challenge
    """
    return AnalyticsService.get_time_spent_per_challenge(db, limit)


@router.get("/completion-by-topic", response_model=list[TopicCompletionStats])
def get_topic_completion_rates(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get completion rates by topic/category (admin only)

    Args:
        admin: Verified admin user
        db: Database session

    Returns:
        List[TopicCompletionStats]: Completion statistics per topic
    """
    return AnalyticsService.get_completion_rates_by_topic(db)


@router.get("/weekly-active-users", response_model=list[WeeklyActiveUsers])
def get_weekly_active_users_trend(
    weeks: int = 8,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly active users trend (admin only)

    Args:
        weeks: Number of weeks to analyze
        admin: Verified admin user
        db: Database session

    Returns:
        List[WeeklyActiveUsers]: Weekly active user counts
    """
    return AnalyticsService.get_weekly_active_users(db, weeks)


@router.get("/xp-distribution", response_model=XPDistribution)
def get_xp_distribution_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get XP distribution across users (admin only)

    Args:
        admin: Verified admin user
        db: Database session

    Returns:
        XPDistribution: XP distribution statistics
    """
    return AnalyticsService.get_xp_distribution(db)


# User endpoints (non-admin) for session tracking

@router.post("/session/start", response_model=SessionResponse)
def start_challenge_session(
    request: SessionStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start tracking a challenge session

    Called when user opens a challenge in the arena

    Args:
        request: Session start request
        current_user: Current authenticated user
        db: Database session

    Returns:
        SessionResponse: Created session
    """
    session = AnalyticsService.start_challenge_session(
        db,
        current_user.id,
        request.challenge_id
    )
    return session


@router.post("/session/end")
def end_challenge_session(
    request: SessionEnd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End a challenge session and record time spent

    Called when user submits or leaves a challenge

    Args:
        request: Session end request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    AnalyticsService.end_challenge_session(
        db,
        request.session_id,
        request.completed,
        request.code,
        request.hints_used
    )
    return {"message": "Session ended successfully"}
