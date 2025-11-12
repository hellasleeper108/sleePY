"""
Challenge endpoints - CRUD operations for coding challenges
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security import get_current_user, get_current_superuser
from app.db.session import get_db
from app.models.user import User
from app.models.challenge import Challenge, DifficultyLevel, ChallengeCategory
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeAdminResponse,
    ChallengeListResponse
)

router = APIRouter()


@router.get("/", response_model=ChallengeListResponse)
def get_challenges(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    difficulty: Optional[DifficultyLevel] = None,
    category: Optional[ChallengeCategory] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of challenges with pagination and filters

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page
        difficulty: Filter by difficulty level
        category: Filter by category
        current_user: Current authenticated user
        db: Database session

    Returns:
        ChallengeListResponse: Paginated list of challenges
    """
    # Build query
    query = db.query(Challenge).filter(Challenge.is_active == True)

    # Apply filters
    if difficulty:
        query = query.filter(Challenge.difficulty == difficulty)

    if category:
        query = query.filter(Challenge.category == category)

    # Filter by user level - only show challenges they can access
    query = query.filter(Challenge.required_level <= current_user.level)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    challenges = query.order_by(Challenge.order, Challenge.id).offset(offset).limit(page_size).all()

    return ChallengeListResponse(
        challenges=[ChallengeResponse.model_validate(c) for c in challenges],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{challenge_id}", response_model=ChallengeResponse)
def get_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific challenge by ID

    Args:
        challenge_id: Challenge ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        ChallengeResponse: Challenge details

    Raises:
        HTTPException: If challenge not found or user level too low
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    if not challenge.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not available"
        )

    # Check if user has required level
    if challenge.required_level > current_user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Challenge requires level {challenge.required_level}. You are level {current_user.level}."
        )

    return ChallengeResponse.model_validate(challenge)


@router.post("/", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a new challenge (admin only)

    Args:
        challenge_data: Challenge creation data
        current_user: Current superuser
        db: Database session

    Returns:
        ChallengeResponse: Created challenge
    """
    new_challenge = Challenge(
        title=challenge_data.title,
        description=challenge_data.description,
        instructions=challenge_data.instructions,
        difficulty=challenge_data.difficulty,
        category=challenge_data.category,
        starter_code=challenge_data.starter_code,
        solution=challenge_data.solution,
        test_cases=challenge_data.test_cases,
        xp_reward=challenge_data.xp_reward,
        required_level=challenge_data.required_level,
        order=challenge_data.order,
        is_active=True
    )

    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)

    return ChallengeResponse.model_validate(new_challenge)


@router.put("/{challenge_id}", response_model=ChallengeResponse)
def update_challenge(
    challenge_id: int,
    challenge_update: ChallengeUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Update a challenge (admin only)

    Args:
        challenge_id: Challenge ID
        challenge_update: Challenge update data
        current_user: Current superuser
        db: Database session

    Returns:
        ChallengeResponse: Updated challenge

    Raises:
        HTTPException: If challenge not found
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Update fields if provided
    update_data = challenge_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(challenge, field, value)

    db.commit()
    db.refresh(challenge)

    return ChallengeResponse.model_validate(challenge)


@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Delete a challenge (admin only)

    Actually performs a soft delete by setting is_active to False

    Args:
        challenge_id: Challenge ID
        current_user: Current superuser
        db: Database session

    Raises:
        HTTPException: If challenge not found
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Soft delete
    challenge.is_active = False
    db.commit()

    return None
