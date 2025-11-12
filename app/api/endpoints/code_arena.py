"""
Code Arena endpoints - Browser-based code execution and validation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.challenge import Challenge
from app.models.progress import Progress
from app.services.code_execution import CodeExecutionService, TestCase
from app.services.game_engine import GameEngine

router = APIRouter()


# Schemas
class ExecutionResult(BaseModel):
    """Result from code execution"""
    output: Any = None
    error: Optional[str] = None


class CodeSubmission(BaseModel):
    """Code submission from frontend"""
    challenge_id: int
    code: str
    execution_results: List[ExecutionResult]


class ValidationResponse(BaseModel):
    """Response after validating code"""
    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    failures: List[Dict]
    message: str
    xp_earned: int = 0
    leveled_up: bool = False
    new_level: Optional[int] = None
    challenge_completed: bool = False


# ==================== CODE ARENA ENDPOINTS ====================

@router.get("/arena", response_class=HTMLResponse)
async def get_code_arena():
    """
    Get the code arena HTML page

    Returns:
        HTML: Code arena interface
    """
    # Read the HTML file
    try:
        with open('/home/user/sleePY/static/code_arena.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code arena page not found"
        )


@router.get("/challenge/{challenge_id}/test-cases")
def get_challenge_test_cases(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test cases for a challenge

    Args:
        challenge_id: Challenge ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Test cases and validation schema

    Raises:
        HTTPException: If challenge not found
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Check level requirement
    if challenge.required_level > current_user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Challenge requires level {challenge.required_level}"
        )

    # Parse test cases
    test_cases = CodeExecutionService.parse_test_cases(
        challenge.test_cases or '[]'
    )

    # Extract function name from starter code
    function_name = CodeExecutionService.extract_function_name(
        challenge.starter_code or ''
    )

    return {
        'challenge_id': challenge.id,
        'title': challenge.title,
        'description': challenge.description,
        'instructions': challenge.instructions,
        'starter_code': challenge.starter_code,
        'function_name': function_name,
        'test_cases': [
            {
                'inputs': tc.inputs,
                'expected_output': tc.expected_output,
                'description': tc.description
            }
            for tc in test_cases
        ],
        'total_tests': len(test_cases),
        'xp_reward': GameEngine.calculate_xp_for_challenge(challenge),
        'difficulty': challenge.difficulty.value
    }


@router.post("/validate", response_model=ValidationResponse)
def validate_code_submission(
    submission: CodeSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate code submission and award XP if successful

    Args:
        submission: Code and execution results
        current_user: Current authenticated user
        db: Database session

    Returns:
        ValidationResponse: Validation result with XP rewards

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

    # Parse expected test cases
    test_cases = CodeExecutionService.parse_test_cases(
        challenge.test_cases or '[]'
    )

    if not test_cases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge has no test cases defined"
        )

    # Validate execution results
    validation_result = CodeExecutionService.validate_execution_result(
        test_cases,
        [result.model_dump() for result in submission.execution_results]
    )

    response = ValidationResponse(
        **validation_result,
        xp_earned=0,
        leveled_up=False,
        challenge_completed=False
    )

    # If all tests passed, award XP and update progress
    if validation_result['success']:
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

        # If not already completed, award XP
        if not progress.is_completed:
            # Calculate XP with difficulty multiplier
            xp_reward = GameEngine.calculate_xp_for_challenge(challenge)

            # Mark as completed
            progress.complete(xp_reward)

            # Award XP
            xp_result = GameEngine.award_xp(current_user, xp_reward, db)

            # Random loot drop
            completed_count = db.query(Progress).filter(
                Progress.user_id == current_user.id,
                Progress.is_completed == True
            ).count()

            if GameEngine.roll_random_chest_drop(completed_count):
                GameEngine.generate_loot_chest(
                    current_user, db,
                    reason=f"Completed: {challenge.title}"
                )

            # Check achievements
            GameEngine.check_and_award_achievements(current_user, db)

            db.commit()
            db.refresh(current_user)

            response.xp_earned = xp_reward
            response.leveled_up = xp_result['leveled_up']
            response.new_level = xp_result['new_level'] if xp_result['leveled_up'] else None
            response.challenge_completed = True

    return response


@router.post("/run-tests")
def run_test_preview(
    challenge_id: int,
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test case information for running in browser

    This doesn't validate or award XP - just returns test structure

    Args:
        challenge_id: Challenge ID
        code: User's code
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Test information for frontend execution
    """
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    # Parse test cases
    test_cases = CodeExecutionService.parse_test_cases(
        challenge.test_cases or '[]'
    )

    # Extract function name
    function_name = CodeExecutionService.extract_function_name(code)

    if not function_name:
        return {
            'error': 'Could not find function definition in code',
            'test_code': None
        }

    # Generate test code
    test_code = CodeExecutionService.generate_test_code(function_name, test_cases)

    return {
        'function_name': function_name,
        'test_code': test_code,
        'test_cases': [
            {
                'inputs': tc.inputs,
                'expected': tc.expected_output,
                'description': tc.description
            }
            for tc in test_cases
        ]
    }
