"""
Progress endpoints - track user completion of challenges
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.challenge import Challenge
from app.models.progress import Progress
from app.schemas.progress import (
    ProgressResponse,
    ProgressWithChallenge,
    SubmitCode,
    SubmissionResult
)

router = APIRouter()


@router.get("/", response_model=list[ProgressWithChallenge])
def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all progress records for current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[ProgressWithChallenge]: List of progress records with challenge info
    """
    progress_records = db.query(Progress).filter(
        Progress.user_id == current_user.id
    ).order_by(Progress.last_attempted_at.desc()).all()

    # Build response with challenge details
    result = []
    for progress in progress_records:
        challenge = progress.challenge
        result.append(ProgressWithChallenge(
            id=progress.id,
            user_id=progress.user_id,
            challenge_id=progress.challenge_id,
            is_completed=progress.is_completed,
            attempts=progress.attempts,
            xp_earned=progress.xp_earned,
            submitted_code=progress.submitted_code,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            last_attempted_at=progress.last_attempted_at,
            challenge_title=challenge.title,
            challenge_difficulty=challenge.difficulty.value,
            challenge_xp_reward=challenge.xp_reward
        ))

    return result


@router.get("/{challenge_id}", response_model=ProgressResponse)
def get_progress_for_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress for a specific challenge

    Args:
        challenge_id: Challenge ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        ProgressResponse: Progress record

    Raises:
        HTTPException: If no progress found
    """
    progress = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.challenge_id == challenge_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this challenge"
        )

    return ProgressResponse.model_validate(progress)


@router.post("/start/{challenge_id}", response_model=ProgressResponse)
def start_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a challenge (create initial progress record)

    Args:
        challenge_id: Challenge ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        ProgressResponse: Created progress record

    Raises:
        HTTPException: If challenge not found or already started
    """
    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Check if user has required level
    if challenge.required_level > current_user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Challenge requires level {challenge.required_level}"
        )

    # Check if already started
    existing = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.challenge_id == challenge_id
    ).first()

    if existing:
        return ProgressResponse.model_validate(existing)

    # Create progress record
    progress = Progress(
        user_id=current_user.id,
        challenge_id=challenge_id,
        is_completed=False,
        attempts=0,
        xp_earned=0
    )

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return ProgressResponse.model_validate(progress)


@router.post("/submit", response_model=SubmissionResult)
def submit_challenge_code(
    submission: SubmitCode,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit code for a challenge

    This is a simplified version. In production, you'd want to:
    - Run the code in a sandboxed environment
    - Execute test cases
    - Validate output

    For now, this marks any submission as successful for demo purposes

    Args:
        submission: Code submission
        current_user: Current authenticated user
        db: Database session

    Returns:
        SubmissionResult: Submission result with XP and level info

    Raises:
        HTTPException: If challenge not found
    """
    # Get challenge
    challenge = db.query(Challenge).filter(
        Challenge.id == submission.challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Get or create progress
    progress = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.challenge_id == submission.challenge_id
    ).first()

    if not progress:
        progress = Progress(
            user_id=current_user.id,
            challenge_id=submission.challenge_id,
            is_completed=False,
            attempts=0,
            xp_earned=0
        )
        db.add(progress)

    # Record attempt
    progress.record_attempt(submission.code)

    # Simple validation - in production, run actual tests
    # For demo, we'll mark as complete if code is not empty
    is_valid = len(submission.code.strip()) > 10

    if is_valid and not progress.is_completed:
        # Mark as completed
        progress.complete(challenge.xp_reward)

        # Award XP to user
        leveled_up = current_user.add_xp(challenge.xp_reward)

        db.commit()
        db.refresh(current_user)

        return SubmissionResult(
            success=True,
            message="Challenge completed successfully!",
            xp_earned=challenge.xp_reward,
            leveled_up=leveled_up,
            new_level=current_user.level if leveled_up else None,
            attempts=progress.attempts
        )
    elif is_valid:
        db.commit()
        return SubmissionResult(
            success=True,
            message="Code submitted (already completed)",
            xp_earned=0,
            leveled_up=False,
            attempts=progress.attempts
        )
    else:
        db.commit()
        return SubmissionResult(
            success=False,
            message="Code validation failed. Please try again.",
            xp_earned=0,
            leveled_up=False,
            attempts=progress.attempts
        )


@router.get("/completed", response_model=list[ProgressWithChallenge])
def get_completed_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all completed challenges for current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[ProgressWithChallenge]: List of completed challenges
    """
    progress_records = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.is_completed == True
    ).order_by(Progress.completed_at.desc()).all()

    # Build response
    result = []
    for progress in progress_records:
        challenge = progress.challenge
        result.append(ProgressWithChallenge(
            id=progress.id,
            user_id=progress.user_id,
            challenge_id=progress.challenge_id,
            is_completed=progress.is_completed,
            attempts=progress.attempts,
            xp_earned=progress.xp_earned,
            submitted_code=progress.submitted_code,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            last_attempted_at=progress.last_attempted_at,
            challenge_title=challenge.title,
            challenge_difficulty=challenge.difficulty.value,
            challenge_xp_reward=challenge.xp_reward
        ))

    return result
