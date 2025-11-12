"""
Mentor AI service - provides intelligent hints for challenges

Uses configurable AI providers to give personalized, progressive hints
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.challenge import Challenge
from app.models.hint import Hint
from app.models.progress import Progress
from app.models.user import User
from app.services.ai_providers import LLMProviderFactory, AIProvider, BaseLLMProvider
import os


class MentorService:
    """
    AI Mentor service for providing hints

    Features:
    - Progressive hints (gets more specific with each request)
    - Context-aware based on user's attempts
    - Configurable AI provider
    - Bonus XP calculation
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        """
        Initialize mentor service

        Args:
            provider: Optional AI provider (auto-detects if None)
        """
        if provider:
            self.provider = provider
        else:
            # Get provider from environment or use auto-detection
            provider_name = os.getenv("AI_PROVIDER", "auto")
            if provider_name == "auto":
                self.provider = LLMProviderFactory.get_available_provider()
            else:
                try:
                    provider_type = AIProvider(provider_name.lower())
                    self.provider = LLMProviderFactory.create_provider(provider_type)
                except ValueError:
                    self.provider = LLMProviderFactory.get_available_provider()

    async def get_hint(
        self,
        user: User,
        challenge: Challenge,
        user_code: Optional[str],
        error_message: Optional[str],
        db: Session
    ) -> Dict[str, Any]:
        """
        Get a hint for a challenge

        Args:
            user: User requesting hint
            challenge: Challenge to get hint for
            user_code: User's current code attempt
            error_message: Error message if any
            db: Database session

        Returns:
            dict: Hint information including text, hint number, and bonus XP info
        """
        # Get previous hints for this user+challenge
        previous_hints = db.query(Hint).filter(
            Hint.user_id == user.id,
            Hint.challenge_id == challenge.id
        ).order_by(Hint.created_at).all()

        hint_number = len(previous_hints) + 1

        # Get user's attempt history
        progress = db.query(Progress).filter(
            Progress.user_id == user.id,
            Progress.challenge_id == challenge.id
        ).first()

        attempt_count = progress.attempts if progress else 0

        # Generate hint using AI
        hint_text = await self._generate_hint(
            challenge=challenge,
            user_code=user_code,
            error_message=error_message,
            hint_number=hint_number,
            attempt_count=attempt_count,
            previous_hints=[h.hint_text for h in previous_hints]
        )

        # Save hint to database
        hint = Hint(
            user_id=user.id,
            challenge_id=challenge.id,
            hint_text=hint_text,
            hint_number=hint_number,
            user_code=user_code,
            error_message=error_message,
            ai_provider=self.provider.__class__.__name__
        )
        db.add(hint)
        db.commit()
        db.refresh(hint)

        # Calculate bonus XP info
        bonus_multiplier = Hint.calculate_bonus_xp_multiplier(hint_number)
        bonus_percentage = int((bonus_multiplier - 1.0) * 100)

        return {
            "hint_id": hint.id,
            "hint_text": hint_text,
            "hint_number": hint_number,
            "total_hints": hint_number,
            "bonus_multiplier": bonus_multiplier,
            "bonus_percentage": bonus_percentage,
            "message": self._get_encouragement_message(hint_number)
        }

    async def _generate_hint(
        self,
        challenge: Challenge,
        user_code: Optional[str],
        error_message: Optional[str],
        hint_number: int,
        attempt_count: int,
        previous_hints: list[str]
    ) -> str:
        """
        Generate hint using AI provider

        Args:
            challenge: Challenge details
            user_code: User's code
            error_message: Error message
            hint_number: Which hint number this is
            attempt_count: How many attempts user has made
            previous_hints: Previous hints given

        Returns:
            str: Generated hint
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(hint_number)

        # Build user prompt
        user_prompt = self._build_user_prompt(
            challenge=challenge,
            user_code=user_code,
            error_message=error_message,
            hint_number=hint_number,
            attempt_count=attempt_count,
            previous_hints=previous_hints
        )

        # Generate hint
        hint = await self.provider.generate_completion(
            prompt=user_prompt,
            max_tokens=300,
            temperature=0.7,
            system_prompt=system_prompt
        )

        return hint.strip()

    def _build_system_prompt(self, hint_number: int) -> str:
        """Build system prompt for AI"""
        base_prompt = """You are a patient and encouraging Python programming mentor.
Your goal is to help students learn by giving hints, NOT direct solutions.

Guidelines:
- Ask leading questions to guide their thinking
- Point out concepts they should review
- Suggest what to focus on, not how to code it
- Be encouraging and supportive
- Keep hints concise (2-3 sentences max)
- Never give complete code solutions
"""

        if hint_number == 1:
            return base_prompt + "\n- This is their FIRST hint, so be subtle and general"
        elif hint_number == 2:
            return base_prompt + "\n- This is their SECOND hint, be more specific about the approach"
        else:
            return base_prompt + "\n- This is hint #" + str(hint_number) + ", you can be more direct while still not giving the answer"

    def _build_user_prompt(
        self,
        challenge: Challenge,
        user_code: Optional[str],
        error_message: Optional[str],
        hint_number: int,
        attempt_count: int,
        previous_hints: list[str]
    ) -> str:
        """Build user prompt with context"""
        prompt = f"""Challenge: {challenge.title}
Difficulty: {challenge.difficulty.value}

Description: {challenge.description}

Instructions: {challenge.instructions}

"""

        if user_code:
            prompt += f"Student's current code:\n```python\n{user_code}\n```\n\n"

        if error_message:
            prompt += f"Error they're getting:\n{error_message}\n\n"

        if attempt_count > 0:
            prompt += f"Number of attempts: {attempt_count}\n\n"

        if previous_hints:
            prompt += "Previous hints given:\n"
            for i, prev_hint in enumerate(previous_hints, 1):
                prompt += f"{i}. {prev_hint}\n"
            prompt += "\n"

        if hint_number == 1:
            prompt += "Give a subtle first hint to point them in the right direction."
        elif hint_number == 2:
            prompt += "Give a more specific second hint about the approach they should take."
        else:
            prompt += f"Give hint #{hint_number}. They're struggling, so be more specific while still making them think."

        return prompt

    def _get_encouragement_message(self, hint_number: int) -> str:
        """Get encouraging message based on hint number"""
        if hint_number == 1:
            return "Great job asking for help! Remember, fewer hints = bonus XP!"
        elif hint_number == 2:
            return "You're on the right track! One more try before your bonus decreases."
        elif hint_number == 3:
            return "Keep trying! You've got this!"
        else:
            return "Don't give up! Learning is a journey, not a race."

    @staticmethod
    def get_hint_statistics(user_id: int, challenge_id: int, db: Session) -> Dict[str, Any]:
        """
        Get hint statistics for a user on a challenge

        Args:
            user_id: User ID
            challenge_id: Challenge ID
            db: Database session

        Returns:
            dict: Hint statistics
        """
        hints = db.query(Hint).filter(
            Hint.user_id == user_id,
            Hint.challenge_id == challenge_id
        ).all()

        hint_count = len(hints)
        bonus_multiplier = Hint.calculate_bonus_xp_multiplier(hint_count)
        bonus_percentage = int((bonus_multiplier - 1.0) * 100)

        return {
            "total_hints": hint_count,
            "bonus_multiplier": bonus_multiplier,
            "bonus_percentage": bonus_percentage,
            "can_still_get_bonus": hint_count < 3,
            "hints_used": [
                {
                    "hint_number": h.hint_number,
                    "created_at": h.created_at.isoformat(),
                    "had_code": bool(h.user_code),
                    "had_error": bool(h.error_message)
                }
                for h in hints
            ]
        }
