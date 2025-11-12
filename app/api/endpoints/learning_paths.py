"""
Learning Path endpoints - structured learning courses
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user, get_current_superuser
from app.db.session import get_db
from app.models.user import User
from app.models.learning_path import LearningPath, PathTopic, PathDifficulty
from app.models.lesson import Lesson
from app.models.user_path_progress import UserPathProgress
from app.models.user_lesson_progress import UserLessonProgress
from app.schemas.learning_path import (
    LearningPathResponse,
    LearningPathWithLessons,
    LearningPathDetail,
    LearningPathCreate,
    LearningPathUpdate,
    LessonResponse,
    LessonCreate,
    PathProgressResponse,
    LessonProgressResponse,
    CompleteLessonResult,
    PathCompletionResult
)
from app.services.game_engine import GameEngine

router = APIRouter()


# ==================== LEARNING PATH ENDPOINTS ====================

@router.get("/", response_model=List[LearningPathWithLessons])
def get_learning_paths(
    topic: Optional[PathTopic] = None,
    difficulty: Optional[PathDifficulty] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all learning paths with lesson previews

    Args:
        topic: Filter by topic
        difficulty: Filter by difficulty
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[LearningPathWithLessons]: List of learning paths
    """
    query = db.query(LearningPath).filter(LearningPath.is_active == True)

    # Apply filters
    if topic:
        query = query.filter(LearningPath.topic == topic)

    if difficulty:
        query = query.filter(LearningPath.difficulty == difficulty)

    # Filter by user level
    query = query.filter(LearningPath.required_level <= current_user.level)

    paths = query.order_by(LearningPath.order, LearningPath.id).all()

    # Build response with lesson previews
    result = []
    for path in paths:
        result.append(LearningPathWithLessons(
            **LearningPathResponse.model_validate(path).model_dump(),
            lessons=[lesson.to_dict_preview() for lesson in path.lessons],
            challenge_count=len(path.challenges)
        ))

    return result


@router.get("/{path_id}", response_model=LearningPathDetail)
def get_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific learning path with all lessons and challenges

    Args:
        path_id: Path ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        LearningPathDetail: Full path details

    Raises:
        HTTPException: If path not found or user level too low
    """
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()

    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )

    if not path.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not available"
        )

    # Check if user has required level
    if path.required_level > current_user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Path requires level {path.required_level}. You are level {current_user.level}."
        )

    return LearningPathDetail(
        **LearningPathResponse.model_validate(path).model_dump(),
        lessons=[LessonResponse.model_validate(lesson) for lesson in path.lessons],
        challenge_ids=[c.id for c in path.challenges]
    )


@router.post("/{path_id}/start", response_model=PathProgressResponse)
def start_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a learning path

    Args:
        path_id: Path ID to start
        current_user: Current authenticated user
        db: Database session

    Returns:
        PathProgressResponse: Created progress record

    Raises:
        HTTPException: If path not found or already started
    """
    # Check if path exists
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()

    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )

    # Check if user has required level
    if path.required_level > current_user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Path requires level {path.required_level}"
        )

    # Check if already started
    existing = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()

    if existing:
        # Return existing progress
        progress_pct = path.get_progress_percentage(current_user.id, db)
        return PathProgressResponse(
            id=existing.id,
            path_id=path.id,
            path_title=path.title,
            path_topic=path.topic.value,
            path_difficulty=path.difficulty.value,
            is_completed=existing.is_completed,
            progress_percentage=progress_pct,
            current_lesson_id=existing.current_lesson_id,
            xp_earned=existing.xp_earned,
            started_at=existing.started_at,
            completed_at=existing.completed_at,
            last_accessed_at=existing.last_accessed_at
        )

    # Create progress record
    progress = UserPathProgress(
        user_id=current_user.id,
        path_id=path_id,
        is_completed=False,
        xp_earned=0
    )

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return PathProgressResponse(
        id=progress.id,
        path_id=path.id,
        path_title=path.title,
        path_topic=path.topic.value,
        path_difficulty=path.difficulty.value,
        is_completed=False,
        progress_percentage=0.0,
        current_lesson_id=None,
        xp_earned=0,
        started_at=progress.started_at,
        completed_at=None,
        last_accessed_at=progress.last_accessed_at
    )


@router.get("/my-progress/all", response_model=List[PathProgressResponse])
def get_user_path_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all learning path progress for current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[PathProgressResponse]: User's path progress
    """
    progress_records = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id
    ).order_by(UserPathProgress.last_accessed_at.desc()).all()

    result = []
    for progress in progress_records:
        path = progress.path
        progress_pct = path.get_progress_percentage(current_user.id, db)

        result.append(PathProgressResponse(
            id=progress.id,
            path_id=path.id,
            path_title=path.title,
            path_topic=path.topic.value,
            path_difficulty=path.difficulty.value,
            is_completed=progress.is_completed,
            progress_percentage=progress_pct,
            current_lesson_id=progress.current_lesson_id,
            xp_earned=progress.xp_earned,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            last_accessed_at=progress.last_accessed_at
        ))

    return result


# ==================== LESSON ENDPOINTS ====================

@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific lesson with full content

    Args:
        lesson_id: Lesson ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        LessonResponse: Lesson with full content

    Raises:
        HTTPException: If lesson not found or user doesn't have access
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # Check if user has access to the path
    path = lesson.path
    if path.required_level > current_user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Path requires level {path.required_level}"
        )

    # Update user's path progress position
    path_progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path.id
    ).first()

    if path_progress:
        path_progress.update_position(lesson_id)
        db.commit()

    return LessonResponse.model_validate(lesson)


@router.post("/lessons/{lesson_id}/complete", response_model=CompleteLessonResult)
def complete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a lesson as completed

    Args:
        lesson_id: Lesson ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        CompleteLessonResult: Completion result with rewards

    Raises:
        HTTPException: If lesson not found or already completed
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # Get or create lesson progress
    lesson_progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson_id
    ).first()

    if lesson_progress and lesson_progress.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson already completed"
        )

    if not lesson_progress:
        lesson_progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id
        )
        db.add(lesson_progress)

    # Mark as completed
    lesson_progress.complete(lesson.xp_reward)

    # Award XP
    xp_result = GameEngine.award_xp(current_user, lesson.xp_reward, db)

    # Update path progress
    path_progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == lesson.path_id
    ).first()

    if path_progress:
        path_progress.xp_earned += lesson.xp_reward

    # Check if path is completed
    path_completed = False
    path_completion_reward = None

    if path_progress:
        progress_pct = lesson.path.get_progress_percentage(current_user.id, db)

        if progress_pct >= 100 and not path_progress.is_completed:
            # Complete the path
            path_completed = True
            path_progress.complete(lesson.path.xp_reward)

            # Award path completion XP
            path_xp_result = GameEngine.award_xp(current_user, lesson.path.xp_reward, db)

            path_completion_reward = {
                "xp_earned": lesson.path.xp_reward,
                "leveled_up": path_xp_result["leveled_up"],
                "new_level": path_xp_result["new_level"] if path_xp_result["leveled_up"] else None
            }

            # Award badge if specified
            if lesson.path.badge_id:
                from app.models.user_badge import UserBadge
                user_badge = UserBadge(
                    user_id=current_user.id,
                    badge_id=lesson.path.badge_id
                )
                db.add(user_badge)
                path_completion_reward["badge_id"] = lesson.path.badge_id

    # Check achievements
    new_achievements = GameEngine.check_and_award_achievements(current_user, db)

    db.commit()
    db.refresh(current_user)

    return CompleteLessonResult(
        lesson_id=lesson_id,
        xp_earned=lesson.xp_reward,
        total_xp=current_user.xp,
        leveled_up=xp_result["leveled_up"],
        new_level=xp_result["new_level"] if xp_result["leveled_up"] else None,
        path_completed=path_completed,
        path_completion_reward=path_completion_reward
    )


# ==================== ADMIN ENDPOINTS ====================

@router.post("/", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
def create_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a new learning path (admin only)

    Args:
        path_data: Path creation data
        current_user: Current superuser
        db: Database session

    Returns:
        LearningPathResponse: Created path
    """
    new_path = LearningPath(**path_data.model_dump())
    db.add(new_path)
    db.commit()
    db.refresh(new_path)

    return LearningPathResponse.model_validate(new_path)


@router.post("/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a new lesson (admin only)

    Args:
        lesson_data: Lesson creation data
        current_user: Current superuser
        db: Database session

    Returns:
        LessonResponse: Created lesson
    """
    new_lesson = Lesson(**lesson_data.model_dump())
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return LessonResponse.model_validate(new_lesson)
