"""
Leaderboard endpoints - Global, weekly, and topic-based rankings
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.challenge import ChallengeCategory
from app.schemas.community import (
    LeaderboardResponse,
    LeaderboardEntry,
    WeeklyLeaderboardEntry,
    TopicLeaderboardEntry,
    UserRankResponse
)
from app.services.leaderboard import LeaderboardService

router = APIRouter()


# ==================== LEADERBOARD ENDPOINTS ====================

@router.get("/global", response_model=LeaderboardResponse)
def get_global_leaderboard(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Results per page")
):
    """
    Get global leaderboard based on total XP

    Cached for 5 minutes, auto-updates when users earn XP

    Args:
        db: Database session
        current_user: Current authenticated user (optional)
        page: Page number for pagination
        page_size: Results per page

    Returns:
        LeaderboardResponse: Global leaderboard
    """
    offset = (page - 1) * page_size
    entries = LeaderboardService.get_global_leaderboard(db, limit=page_size, offset=offset)

    # Get user's rank if authenticated
    user_rank = None
    if current_user:
        user_rank = LeaderboardService.get_user_rank(db, current_user.id, 'global')

    # Convert to LeaderboardEntry objects
    leaderboard_entries = [
        LeaderboardEntry(**entry) for entry in entries
    ]

    return LeaderboardResponse(
        leaderboard_type='global',
        entries=leaderboard_entries,
        total_count=len(entries),
        current_page=page,
        page_size=page_size,
        user_rank=user_rank
    )


@router.get("/weekly", response_model=LeaderboardResponse)
def get_weekly_leaderboard(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Results per page")
):
    """
    Get weekly leaderboard based on XP earned in last 7 days

    Resets weekly, cached for 5 minutes

    Args:
        db: Database session
        current_user: Current authenticated user (optional)
        page: Page number for pagination
        page_size: Results per page

    Returns:
        LeaderboardResponse: Weekly leaderboard
    """
    offset = (page - 1) * page_size
    entries = LeaderboardService.get_weekly_leaderboard(db, limit=page_size, offset=offset)

    # Get user's rank if authenticated
    user_rank = None
    if current_user:
        user_rank = LeaderboardService.get_user_rank(db, current_user.id, 'weekly')

    # Convert to WeeklyLeaderboardEntry objects
    leaderboard_entries = [
        WeeklyLeaderboardEntry(**entry) for entry in entries
    ]

    return LeaderboardResponse(
        leaderboard_type='weekly',
        entries=leaderboard_entries,
        total_count=len(entries),
        current_page=page,
        page_size=page_size,
        user_rank=user_rank
    )


@router.get("/topic/{category}", response_model=LeaderboardResponse)
def get_topic_leaderboard(
    category: ChallengeCategory,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Results per page")
):
    """
    Get topic-based leaderboard for specific challenge category

    Tracks XP earned in specific category (basics, data_structures, etc.)

    Args:
        category: Challenge category
        db: Database session
        current_user: Current authenticated user (optional)
        page: Page number for pagination
        page_size: Results per page

    Returns:
        LeaderboardResponse: Topic leaderboard
    """
    offset = (page - 1) * page_size
    entries = LeaderboardService.get_topic_leaderboard(
        db, category, limit=page_size, offset=offset
    )

    # Convert to TopicLeaderboardEntry objects
    leaderboard_entries = [
        TopicLeaderboardEntry(**entry) for entry in entries
    ]

    return LeaderboardResponse(
        leaderboard_type=f'topic_{category.value}',
        entries=leaderboard_entries,
        total_count=len(entries),
        current_page=page,
        page_size=page_size,
        user_rank=None  # Topic rank calculation would be expensive
    )


@router.get("/my-rank", response_model=UserRankResponse)
def get_my_rank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's rank across different leaderboards

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserRankResponse: User's ranks
    """
    global_rank = LeaderboardService.get_user_rank(db, current_user.id, 'global')
    weekly_rank = LeaderboardService.get_user_rank(db, current_user.id, 'weekly')

    # Get total number of active users
    total_users = db.query(User).filter(User.is_active == True).count()

    return UserRankResponse(
        user_id=current_user.id,
        global_rank=global_rank,
        weekly_rank=weekly_rank,
        total_users=total_users
    )


@router.post("/invalidate-cache")
def invalidate_leaderboard_cache(
    current_user: User = Depends(get_current_user),
    leaderboard_type: Optional[str] = Query(None, description="Specific type to invalidate")
):
    """
    Invalidate leaderboard cache (admin/testing only)

    Args:
        current_user: Current authenticated user
        leaderboard_type: Optional specific type to invalidate

    Returns:
        dict: Success message
    """
    # In production, add admin check here
    LeaderboardService.invalidate_cache(leaderboard_type)

    return {
        "message": f"Cache invalidated for {leaderboard_type or 'all leaderboards'}"
    }
