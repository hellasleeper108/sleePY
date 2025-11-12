"""
Mentor AI endpoints - intelligent hints for challenges
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.challenge import Challenge
from app.models.hint import Hint
from app.schemas.mentor import (
    HintRequest,
    HintResponse,
    HintStatistics,
    MentorConfig,
    ProviderStatus
)
from app.services.mentor import MentorService
from app.services.ai_providers import (
    LLMProviderFactory,
    AIProvider,
    OllamaProvider,
    OpenAIProvider,
    ClaudeProvider,
    MockProvider
)

router = APIRouter()

# Create mentor service instance
mentor_service = MentorService()


# ==================== MENTOR ENDPOINTS ====================

@router.post("/hint", response_model=HintResponse)
async def get_hint(
    request: HintRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an AI-generated hint for a challenge

    The mentor provides progressive hints:
    - 1st hint: Subtle, general guidance
    - 2nd hint: More specific approach
    - 3+ hints: Increasingly direct

    Bonus XP system:
    - 0 hints: +20% bonus XP
    - 1 hint: +10% bonus XP
    - 2 hints: +5% bonus XP
    - 3+ hints: No bonus

    Args:
        request: Hint request with challenge_id and optional code/error
        current_user: Current authenticated user
        db: Database session

    Returns:
        HintResponse: Generated hint with bonus info

    Raises:
        HTTPException: If challenge not found
    """
    # Get challenge
    challenge = db.query(Challenge).filter(
        Challenge.id == request.challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Check if user meets level requirement
    if challenge.required_level > current_user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Challenge requires level {challenge.required_level}"
        )

    # Generate hint
    try:
        hint_data = await mentor_service.get_hint(
            user=current_user,
            challenge=challenge,
            user_code=request.user_code,
            error_message=request.error_message,
            db=db
        )

        return HintResponse(**hint_data)

    except Exception as e:
        # If AI fails, provide a generic fallback hint
        fallback_hint = f"""Here's a hint to help you with this {challenge.difficulty.value} challenge:

1. Review the challenge description carefully
2. Think about what Python concepts are needed
3. Start with a simple solution, then optimize
4. Test with the example inputs

You're doing great! Keep trying!"""

        # Still record the hint attempt
        hint_count = db.query(Hint).filter(
            Hint.user_id == current_user.id,
            Hint.challenge_id == challenge.id
        ).count()

        hint_number = hint_count + 1

        hint = Hint(
            user_id=current_user.id,
            challenge_id=challenge.id,
            hint_text=fallback_hint,
            hint_number=hint_number,
            user_code=request.user_code,
            error_message=request.error_message,
            ai_provider="fallback"
        )
        db.add(hint)
        db.commit()

        bonus_multiplier = Hint.calculate_bonus_xp_multiplier(hint_number)
        bonus_percentage = int((bonus_multiplier - 1.0) * 100)

        return HintResponse(
            hint_id=hint.id,
            hint_text=fallback_hint,
            hint_number=hint_number,
            total_hints=hint_number,
            bonus_multiplier=bonus_multiplier,
            bonus_percentage=bonus_percentage,
            message="Hint provided (AI temporarily unavailable)"
        )


@router.get("/statistics/{challenge_id}", response_model=HintStatistics)
def get_hint_statistics(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get hint statistics for a challenge

    Shows:
    - Number of hints used
    - Current bonus XP multiplier
    - Whether bonus is still available
    - History of hints requested

    Args:
        challenge_id: Challenge ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        HintStatistics: Hint statistics and bonus info
    """
    stats = MentorService.get_hint_statistics(
        user_id=current_user.id,
        challenge_id=challenge_id,
        db=db
    )

    return HintStatistics(**stats)


@router.get("/config", response_model=MentorConfig)
def get_mentor_config():
    """
    Get mentor configuration and provider status

    Shows which AI providers are available and which is active

    Returns:
        MentorConfig: Configuration information
    """
    # Check all providers
    providers = [
        ("Ollama (Local)", OllamaProvider()),
        ("OpenAI GPT", OpenAIProvider()),
        ("Anthropic Claude", ClaudeProvider()),
        ("Mock (Testing)", MockProvider()),
    ]

    provider_statuses = []
    active_provider_name = mentor_service.provider.__class__.__name__

    for name, provider in providers:
        provider_statuses.append(
            ProviderStatus(
                provider_name=name,
                is_available=provider.is_available(),
                is_active=provider.__class__.__name__ == active_provider_name
            )
        )

    return MentorConfig(
        current_provider=active_provider_name,
        available_providers=provider_statuses,
        bonus_xp_enabled=True
    )


@router.get("/available")
def check_mentor_available():
    """
    Quick check if mentor is available

    Returns:
        dict: Availability status
    """
    is_available = mentor_service.provider.is_available()

    return {
        "available": is_available,
        "provider": mentor_service.provider.__class__.__name__,
        "message": "Mentor is ready to help!" if is_available else "Mentor temporarily unavailable"
    }


@router.get("/hints/history")
def get_all_hints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get user's hint history across all challenges

    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum hints to return

    Returns:
        dict: Hint history with challenge info
    """
    hints = (
        db.query(Hint)
        .filter(Hint.user_id == current_user.id)
        .order_by(Hint.created_at.desc())
        .limit(limit)
        .all()
    )

    # Get challenge info for each hint
    hint_history = []
    for hint in hints:
        challenge = db.query(Challenge).filter(Challenge.id == hint.challenge_id).first()

        hint_history.append({
            "hint_id": hint.id,
            "challenge_id": hint.challenge_id,
            "challenge_title": challenge.title if challenge else "Unknown",
            "hint_number": hint.hint_number,
            "created_at": hint.created_at.isoformat(),
            "ai_provider": hint.ai_provider,
        })

    return {
        "total_hints": len(hints),
        "hints": hint_history
    }
