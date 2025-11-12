"""
Badge endpoints - manage achievements and badges
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import get_current_user, get_current_superuser
from app.db.session import get_db
from app.models.user import User
from app.models.badge import Badge, UserBadge
from app.schemas.badge import BadgeCreate, BadgeResponse, UserBadgeResponse

router = APIRouter()


@router.get("/", response_model=list[BadgeResponse])
def get_all_badges(db: Session = Depends(get_db)):
    """
    Get all available badges

    Args:
        db: Database session

    Returns:
        list[BadgeResponse]: List of all badges
    """
    badges = db.query(Badge).order_by(Badge.name).all()
    return [BadgeResponse.model_validate(badge) for badge in badges]


@router.get("/my-badges", response_model=list[UserBadgeResponse])
def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all badges earned by current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[UserBadgeResponse]: List of user's badges
    """
    user_badges = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).order_by(UserBadge.earned_at.desc()).all()

    result = []
    for user_badge in user_badges:
        badge = user_badge.badge
        result.append(UserBadgeResponse(
            id=user_badge.id,
            badge_id=badge.id,
            badge_name=badge.name,
            badge_description=badge.description,
            badge_icon=badge.icon,
            earned_at=user_badge.earned_at
        ))

    return result


@router.get("/{badge_id}", response_model=BadgeResponse)
def get_badge(badge_id: int, db: Session = Depends(get_db)):
    """
    Get a specific badge by ID

    Args:
        badge_id: Badge ID
        db: Database session

    Returns:
        BadgeResponse: Badge details

    Raises:
        HTTPException: If badge not found
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()

    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )

    return BadgeResponse.model_validate(badge)


@router.post("/", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
def create_badge(
    badge_data: BadgeCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a new badge (admin only)

    Args:
        badge_data: Badge creation data
        current_user: Current superuser
        db: Database session

    Returns:
        BadgeResponse: Created badge

    Raises:
        HTTPException: If badge name already exists
    """
    # Check if badge name exists
    existing = db.query(Badge).filter(Badge.name == badge_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Badge with this name already exists"
        )

    new_badge = Badge(
        name=badge_data.name,
        description=badge_data.description,
        icon=badge_data.icon,
        criteria=badge_data.criteria
    )

    db.add(new_badge)
    db.commit()
    db.refresh(new_badge)

    return BadgeResponse.model_validate(new_badge)


@router.post("/award/{user_id}/{badge_id}", response_model=UserBadgeResponse)
def award_badge(
    user_id: int,
    badge_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Award a badge to a user (admin only)

    Args:
        user_id: User ID to award badge to
        badge_id: Badge ID to award
        current_user: Current superuser
        db: Database session

    Returns:
        UserBadgeResponse: Awarded badge record

    Raises:
        HTTPException: If user/badge not found or badge already awarded
    """
    # Check user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check badge exists
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )

    # Check if already awarded
    existing = db.query(UserBadge).filter(
        UserBadge.user_id == user_id,
        UserBadge.badge_id == badge_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Badge already awarded to this user"
        )

    # Award badge
    user_badge = UserBadge(user_id=user_id, badge_id=badge_id)

    try:
        db.add(user_badge)
        db.commit()
        db.refresh(user_badge)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Badge already awarded to this user"
        )

    return UserBadgeResponse(
        id=user_badge.id,
        badge_id=badge.id,
        badge_name=badge.name,
        badge_description=badge.description,
        badge_icon=badge.icon,
        earned_at=user_badge.earned_at
    )


@router.delete("/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_badge(
    badge_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Delete a badge (admin only)

    This will also remove all user badge records

    Args:
        badge_id: Badge ID
        current_user: Current superuser
        db: Database session

    Raises:
        HTTPException: If badge not found
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()

    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )

    db.delete(badge)
    db.commit()

    return None
