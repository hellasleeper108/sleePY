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
from app.models.hint import Hint
from app.schemas.progress import (
    ProgressResponse,
    ProgressWithChallenge,
    SubmitCode,
    SubmissionResult
)
from app.services.game_engine import GameEngine
from app.services.leaderboard import LeaderboardService

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
        # Calculate base XP reward using game engine
        base_xp_reward = GameEngine.calculate_xp_for_challenge(challenge)

        # Check how many hints the user used for this challenge
        hint_count = db.query(Hint).filter(
            Hint.user_id == current_user.id,
            Hint.challenge_id == submission.challenge_id
        ).count()

        # Apply bonus XP multiplier based on self-sufficiency
        bonus_multiplier = Hint.calculate_bonus_xp_multiplier(hint_count)
        xp_reward = int(base_xp_reward * bonus_multiplier)

        # Mark as completed
        progress.complete(xp_reward)

        # Award XP using game engine (handles leveling and rewards)
        xp_result = GameEngine.award_xp(current_user, xp_reward, db)

        # Invalidate leaderboard cache (auto-updates leaderboards)
        LeaderboardService.invalidate_cache()

        # Random loot chest drop
        loot_dropped = None
        completed_count = db.query(Progress).filter(
            Progress.user_id == current_user.id,
            Progress.is_completed == True
        ).count()

        if GameEngine.roll_random_chest_drop(completed_count):
            chest = GameEngine.generate_loot_chest(
                current_user, db,
                reason=f"Completed: {challenge.title}"
            )
            loot_dropped = {
                "chest_id": chest.id,
                "rarity": chest.rarity.value
            }

        # Check and award achievements
        new_achievements = GameEngine.check_and_award_achievements(current_user, db)

        db.commit()
        db.refresh(current_user)

        result = SubmissionResult(
            success=True,
            message="Challenge completed successfully!",
            xp_earned=xp_reward,
            leveled_up=xp_result["leveled_up"],
            new_level=xp_result["new_level"] if xp_result["leveled_up"] else None,
            attempts=progress.attempts
        )

        # Add extra info (not in schema, but useful)
        result_dict = result.model_dump()
        if loot_dropped:
            result_dict["loot_dropped"] = loot_dropped
        if new_achievements:
            result_dict["achievements_unlocked"] = [
                {"name": a.name, "icon": a.icon} for a in new_achievements
            ]
        if xp_result.get("level_up_chest"):
            result_dict["level_up_chest"] = xp_result["level_up_chest"]

        # Add bonus XP information
        if bonus_multiplier > 1.0:
            bonus_percentage = int((bonus_multiplier - 1.0) * 100)
            result_dict["bonus_xp"] = {
                "multiplier": bonus_multiplier,
                "bonus_percentage": bonus_percentage,
                "base_xp": base_xp_reward,
                "total_xp": xp_reward,
                "hints_used": hint_count,
                "message": f"🎉 +{bonus_percentage}% XP bonus for solving with {hint_count} hint{'s' if hint_count != 1 else ''}!"
            }

        return result_dict

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
