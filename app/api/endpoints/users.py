"""
User endpoints - profile, stats, leaderboard
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.progress import Progress
from app.models.badge import UserBadge
from app.schemas.user import UserResponse, UserUpdate, UserStatsResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse: User profile data
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile

    Args:
        user_update: User update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse: Updated user profile
    """
    # Update fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    if user_update.email is not None:
        # Check if email is already taken by another user
        existing = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        current_user.email = user_update.email

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.get("/me/stats", response_model=UserStatsResponse)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user statistics

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserStatsResponse: User stats including XP, level, completed challenges
    """
    # Count completed challenges
    completed_challenges = db.query(func.count(Progress.id)).filter(
        Progress.user_id == current_user.id,
        Progress.is_completed == True
    ).scalar()

    # Count earned badges
    earned_badges = db.query(func.count(UserBadge.id)).filter(
        UserBadge.user_id == current_user.id
    ).scalar()

    return UserStatsResponse(
        id=current_user.id,
        username=current_user.username,
        xp=current_user.xp,
        level=current_user.level,
        xp_for_next_level=current_user.xp_for_next_level(),
        total_challenges_completed=completed_challenges,
        total_badges_earned=earned_badges,
        created_at=current_user.created_at
    )


@router.get("/leaderboard", response_model=list[UserStatsResponse])
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get leaderboard of top users by XP

    Args:
        limit: Number of users to return (default 10, max 100)
        db: Database session

    Returns:
        list[UserStatsResponse]: Top users sorted by XP
    """
    # Limit to max 100
    limit = min(limit, 100)

    # Get top users by XP
    top_users = db.query(User).filter(
        User.is_active == True
    ).order_by(
        User.xp.desc()
    ).limit(limit).all()

    # Build response with stats
    leaderboard = []
    for user in top_users:
        # Count completed challenges
        completed_challenges = db.query(func.count(Progress.id)).filter(
            Progress.user_id == user.id,
            Progress.is_completed == True
        ).scalar()

        # Count earned badges
        earned_badges = db.query(func.count(UserBadge.id)).filter(
            UserBadge.user_id == user.id
        ).scalar()

        leaderboard.append(UserStatsResponse(
            id=user.id,
            username=user.username,
            xp=user.xp,
            level=user.level,
            xp_for_next_level=user.xp_for_next_level(),
            total_challenges_completed=completed_challenges,
            total_badges_earned=earned_badges,
            created_at=user.created_at
        ))

    return leaderboard


@router.get("/{user_id}", response_model=UserStatsResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID (public view)

    Args:
        user_id: User ID
        db: Database session

    Returns:
        UserStatsResponse: User stats

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Count completed challenges
    completed_challenges = db.query(func.count(Progress.id)).filter(
        Progress.user_id == user.id,
        Progress.is_completed == True
    ).scalar()

    # Count earned badges
    earned_badges = db.query(func.count(UserBadge.id)).filter(
        UserBadge.user_id == user.id
    ).scalar()

    return UserStatsResponse(
        id=user.id,
        username=user.username,
        xp=user.xp,
        level=user.level,
        xp_for_next_level=user.xp_for_next_level(),
        total_challenges_completed=completed_challenges,
        total_badges_earned=earned_badges,
        created_at=user.created_at
    )
