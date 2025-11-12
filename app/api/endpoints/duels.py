"""
Duels endpoints - Challenge duel competitions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from datetime import datetime

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.challenge import Challenge
from app.models.duel import Duel, DuelStatus
from app.models.progress import Progress
from app.schemas.community import (
    DuelCreate,
    DuelResponse,
    DuelAccept,
    DuelSubmission,
    DuelResult
)
from app.services.game_engine import GameEngine
from app.services.code_execution import CodeExecutionService

router = APIRouter()


# ==================== DUEL ENDPOINTS ====================

@router.post("/create", response_model=DuelResponse)
def create_duel(
    duel_data: DuelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new duel challenge

    Args:
        duel_data: Duel creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        DuelResponse: Created duel

    Raises:
        HTTPException: If invalid opponent or challenge
    """
    # Can't duel yourself
    if duel_data.opponent_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot challenge yourself to a duel"
        )

    # Check if opponent exists
    opponent = db.query(User).filter(User.id == duel_data.opponent_id).first()
    if not opponent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opponent not found"
        )

    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == duel_data.challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Check for existing active duel between these users on this challenge
    existing = db.query(Duel).filter(
        Duel.challenge_id == duel_data.challenge_id,
        or_(
            and_(
                Duel.challenger_id == current_user.id,
                Duel.opponent_id == duel_data.opponent_id
            ),
            and_(
                Duel.challenger_id == duel_data.opponent_id,
                Duel.opponent_id == current_user.id
            )
        ),
        Duel.status.in_([DuelStatus.PENDING, DuelStatus.ACTIVE])
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active duel already exists for this challenge between these users"
        )

    # Create duel
    duel = Duel(
        challenge_id=duel_data.challenge_id,
        challenger_id=current_user.id,
        opponent_id=duel_data.opponent_id,
        xp_stake=duel_data.xp_stake,
        status=DuelStatus.PENDING
    )
    db.add(duel)
    db.commit()
    db.refresh(duel)

    return _build_duel_response(duel, db)


@router.post("/accept", response_model=DuelResponse)
def accept_duel(
    accept_data: DuelAccept,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a duel challenge

    Args:
        accept_data: Duel accept data
        current_user: Current authenticated user
        db: Database session

    Returns:
        DuelResponse: Updated duel

    Raises:
        HTTPException: If duel not found or not pending
    """
    duel = db.query(Duel).filter(Duel.id == accept_data.duel_id).first()

    if not duel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Duel not found"
        )

    # Only opponent can accept
    if duel.opponent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the challenged opponent can accept this duel"
        )

    if not duel.accept():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duel cannot be accepted (may be expired or already accepted)"
        )

    db.commit()
    db.refresh(duel)

    return _build_duel_response(duel, db)


@router.post("/submit", response_model=DuelResult)
def submit_duel_solution(
    submission: DuelSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit solution for duel challenge

    Args:
        submission: Duel submission data
        current_user: Current authenticated user
        db: Database session

    Returns:
        DuelResult: Duel results

    Raises:
        HTTPException: If invalid submission
    """
    duel = db.query(Duel).filter(Duel.id == submission.duel_id).first()

    if not duel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Duel not found"
        )

    # Check if user is participant
    if current_user.id not in [duel.challenger_id, duel.opponent_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this duel"
        )

    if duel.status != DuelStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duel is not active (status: {duel.status})"
        )

    # Validate solution
    challenge = db.query(Challenge).filter(Challenge.id == duel.challenge_id).first()
    test_cases = CodeExecutionService.parse_test_cases(challenge.test_cases or '[]')

    # For now, we'll assume the code is already validated on frontend
    # In production, you'd want to execute and validate here too

    # Record completion
    is_complete = duel.submit_completion(current_user.id, submission.completion_time)

    if is_complete:
        # Award XP to both users
        challenger = db.query(User).filter(User.id == duel.challenger_id).first()
        opponent = db.query(User).filter(User.id == duel.opponent_id).first()

        if duel.challenger_xp_earned > 0:
            GameEngine.award_xp(challenger, duel.challenger_xp_earned, db)
        if duel.opponent_xp_earned > 0:
            GameEngine.award_xp(opponent, duel.opponent_xp_earned, db)

        # Update progress for both users if not already completed
        for user_id in [duel.challenger_id, duel.opponent_id]:
            progress = db.query(Progress).filter(
                Progress.user_id == user_id,
                Progress.challenge_id == duel.challenge_id
            ).first()

            if not progress:
                progress = Progress(
                    user_id=user_id,
                    challenge_id=duel.challenge_id,
                    is_completed=True,
                    attempts=1,
                    xp_earned=challenge.xp_reward
                )
                db.add(progress)
            elif not progress.is_completed:
                progress.is_completed = True
                progress.xp_earned = challenge.xp_reward

    db.commit()
    db.refresh(duel)

    # Build result
    winner = None
    if duel.winner_id:
        winner = db.query(User).filter(User.id == duel.winner_id).first()

    message = "Solution submitted"
    if is_complete:
        if duel.winner_id == current_user.id:
            message = f"Victory! You won {duel.challenger_xp_earned if current_user.id == duel.challenger_id else duel.opponent_xp_earned} XP!"
        elif duel.winner_id:
            message = f"Challenge completed! You earned {duel.challenger_xp_earned if current_user.id == duel.challenger_id else duel.opponent_xp_earned} XP"
        else:
            message = "Tie! Both earned equal XP"

    return DuelResult(
        duel_id=duel.id,
        status=duel.status,
        winner_id=duel.winner_id,
        winner_username=winner.username if winner else None,
        challenger_time=duel.challenger_completion_time,
        opponent_time=duel.opponent_completion_time,
        challenger_xp=duel.challenger_xp_earned,
        opponent_xp=duel.opponent_xp_earned,
        message=message
    )


@router.get("/my-duels", response_model=List[DuelResponse])
def get_my_duels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: DuelStatus = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get current user's duels

    Args:
        current_user: Current authenticated user
        db: Database session
        status_filter: Optional status filter
        limit: Maximum number of results

    Returns:
        list: User's duels
    """
    query = db.query(Duel).filter(
        or_(
            Duel.challenger_id == current_user.id,
            Duel.opponent_id == current_user.id
        )
    )

    if status_filter:
        query = query.filter(Duel.status == status_filter)

    duels = query.order_by(Duel.created_at.desc()).limit(limit).all()

    return [_build_duel_response(duel, db) for duel in duels]


@router.get("/pending", response_model=List[DuelResponse])
def get_pending_duels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pending duel invitations for current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list: Pending duels where user is opponent
    """
    duels = (
        db.query(Duel)
        .filter(
            Duel.opponent_id == current_user.id,
            Duel.status == DuelStatus.PENDING,
            Duel.expires_at > datetime.utcnow()
        )
        .order_by(Duel.created_at.desc())
        .all()
    )

    return [_build_duel_response(duel, db) for duel in duels]


@router.delete("/cancel/{duel_id}")
def cancel_duel(
    duel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a duel

    Args:
        duel_id: Duel ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If not authorized or cannot cancel
    """
    duel = db.query(Duel).filter(Duel.id == duel_id).first()

    if not duel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Duel not found"
        )

    # Only challenger can cancel
    if duel.challenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the challenger can cancel this duel"
        )

    if not duel.cancel():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duel cannot be cancelled (may be already completed)"
        )

    db.commit()

    return {"message": "Duel cancelled successfully"}


# ==================== HELPER FUNCTIONS ====================

def _build_duel_response(duel: Duel, db: Session) -> DuelResponse:
    """Build DuelResponse from Duel model"""
    challenge = db.query(Challenge).filter(Challenge.id == duel.challenge_id).first()
    challenger = db.query(User).filter(User.id == duel.challenger_id).first()
    opponent = db.query(User).filter(User.id == duel.opponent_id).first()

    time_remaining = None
    if duel.status == DuelStatus.PENDING:
        td = duel.get_time_remaining()
        time_remaining = int(td.total_seconds()) if td else 0

    return DuelResponse(
        id=duel.id,
        challenge_id=duel.challenge_id,
        challenge_title=challenge.title if challenge else None,
        challenger_id=duel.challenger_id,
        challenger_username=challenger.username if challenger else None,
        opponent_id=duel.opponent_id,
        opponent_username=opponent.username if opponent else None,
        status=duel.status,
        xp_stake=duel.xp_stake,
        created_at=duel.created_at,
        accepted_at=duel.accepted_at,
        expires_at=duel.expires_at,
        completed_at=duel.completed_at,
        winner_id=duel.winner_id,
        challenger_completion_time=duel.challenger_completion_time,
        opponent_completion_time=duel.opponent_completion_time,
        challenger_xp_earned=duel.challenger_xp_earned,
        opponent_xp_earned=duel.opponent_xp_earned,
        time_remaining_seconds=time_remaining
    )
