"""
Friends endpoints - Following/follower system
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.friendship import Friendship
from app.models.progress import Progress
from app.schemas.community import (
    FriendshipCreate,
    FriendResponse,
    FriendListResponse,
    UserSearchResponse
)
from app.services.leaderboard import LeaderboardService

router = APIRouter()


# ==================== FRIENDSHIP ENDPOINTS ====================

@router.post("/follow")
def follow_user(
    friendship: FriendshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Follow another user

    Args:
        friendship: Contains following_id
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If trying to follow self or already following
    """
    # Can't follow yourself
    if friendship.following_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )

    # Check if user exists
    target_user = db.query(User).filter(User.id == friendship.following_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already following
    existing = db.query(Friendship).filter(
        Friendship.follower_id == current_user.id,
        Friendship.following_id == friendship.following_id
    ).first()

    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already following this user"
            )
        else:
            # Reactivate friendship
            existing.is_active = True
            db.commit()
            return {"message": f"Now following {target_user.username}"}

    # Create new friendship
    new_friendship = Friendship(
        follower_id=current_user.id,
        following_id=friendship.following_id,
        is_active=True
    )
    db.add(new_friendship)
    db.commit()

    # Invalidate friends leaderboard cache
    LeaderboardService.invalidate_cache('friends_leaderboard')

    return {"message": f"Now following {target_user.username}"}


@router.delete("/unfollow/{user_id}")
def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unfollow a user

    Args:
        user_id: ID of user to unfollow
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If not following user
    """
    friendship = db.query(Friendship).filter(
        Friendship.follower_id == current_user.id,
        Friendship.following_id == user_id,
        Friendship.is_active == True
    ).first()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following this user"
        )

    friendship.is_active = False
    db.commit()

    # Invalidate friends leaderboard cache
    LeaderboardService.invalidate_cache('friends_leaderboard')

    return {"message": "Unfollowed successfully"}


@router.get("/following", response_model=List[FriendResponse])
def get_following(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get list of users the current user is following

    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of results

    Returns:
        list: List of followed users
    """
    friendships = (
        db.query(Friendship, User)
        .join(User, Friendship.following_id == User.id)
        .filter(
            Friendship.follower_id == current_user.id,
            Friendship.is_active == True
        )
        .order_by(Friendship.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        FriendResponse(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            xp=user.xp,
            level=user.level,
            followed_at=friendship.created_at
        )
        for friendship, user in friendships
    ]


@router.get("/followers", response_model=List[FriendResponse])
def get_followers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get list of users following the current user

    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of results

    Returns:
        list: List of followers
    """
    friendships = (
        db.query(Friendship, User)
        .join(User, Friendship.follower_id == User.id)
        .filter(
            Friendship.following_id == current_user.id,
            Friendship.is_active == True
        )
        .order_by(Friendship.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        FriendResponse(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            xp=user.xp,
            level=user.level,
            followed_at=friendship.created_at
        )
        for friendship, user in friendships
    ]


@router.get("/list", response_model=FriendListResponse)
def get_friend_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete friend list (following and followers)

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        FriendListResponse: Complete friend information
    """
    # Get following
    following_data = (
        db.query(Friendship, User)
        .join(User, Friendship.following_id == User.id)
        .filter(
            Friendship.follower_id == current_user.id,
            Friendship.is_active == True
        )
        .order_by(User.xp.desc())
        .all()
    )

    following = [
        FriendResponse(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            xp=user.xp,
            level=user.level,
            followed_at=friendship.created_at
        )
        for friendship, user in following_data
    ]

    # Get followers
    follower_data = (
        db.query(Friendship, User)
        .join(User, Friendship.follower_id == User.id)
        .filter(
            Friendship.following_id == current_user.id,
            Friendship.is_active == True
        )
        .order_by(User.xp.desc())
        .all()
    )

    followers = [
        FriendResponse(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            xp=user.xp,
            level=user.level,
            followed_at=friendship.created_at
        )
        for friendship, user in follower_data
    ]

    return FriendListResponse(
        following=following,
        followers=followers,
        following_count=len(following),
        follower_count=len(followers)
    )


@router.get("/search", response_model=List[UserSearchResponse])
def search_users(
    query: str = Query(..., min_length=1, max_length=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search for users by username or full name

    Args:
        query: Search query
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of results

    Returns:
        list: Matching users
    """
    # Get users matching search
    users = (
        db.query(User)
        .filter(
            User.is_active == True,
            User.id != current_user.id,  # Exclude current user
            or_(
                User.username.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%")
            )
        )
        .order_by(User.xp.desc())
        .limit(limit)
        .all()
    )

    # Get users that current user is following
    following_ids = {
        f.following_id for f in
        db.query(Friendship.following_id).filter(
            Friendship.follower_id == current_user.id,
            Friendship.is_active == True
        ).all()
    }

    return [
        UserSearchResponse(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            xp=user.xp,
            level=user.level,
            is_following=user.id in following_ids
        )
        for user in users
    ]


@router.get("/leaderboard")
def get_friends_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get leaderboard of friends

    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of results

    Returns:
        dict: Friends leaderboard
    """
    leaderboard = LeaderboardService.get_friends_leaderboard(
        db, current_user.id, limit
    )

    return {
        'leaderboard_type': 'friends',
        'entries': leaderboard,
        'total_count': len(leaderboard)
    }
