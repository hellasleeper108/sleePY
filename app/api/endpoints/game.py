"""
Game endpoints - RPG mechanics (loot, streaks, achievements)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.loot_chest import LootChest
from app.models.daily_streak import DailyStreak
from app.models.achievement import Achievement
from app.models.user_achievement import UserAchievement
from app.schemas.game import (
    LootChestResponse,
    OpenChestResult,
    StreakResponse,
    CheckInResult,
    AchievementResponse,
    AchievementProgressResponse,
    UserAchievementResponse,
    GameStatsResponse
)
from app.services.game_engine import GameEngine

router = APIRouter()


# ==================== LOOT CHEST ENDPOINTS ====================

@router.get("/loot-chests", response_model=List[LootChestResponse])
def get_user_loot_chests(
    show_opened: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all loot chests for current user

    Args:
        show_opened: Include opened chests (default: only unopened)
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[LootChestResponse]: User's loot chests
    """
    query = db.query(LootChest).filter(LootChest.user_id == current_user.id)

    if not show_opened:
        query = query.filter(LootChest.is_opened == False)

    chests = query.order_by(LootChest.created_at.desc()).all()

    return [LootChestResponse.model_validate(chest) for chest in chests]


@router.post("/loot-chests/open/{chest_id}", response_model=OpenChestResult)
def open_loot_chest(
    chest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Open a loot chest

    Args:
        chest_id: Chest ID to open
        current_user: Current authenticated user
        db: Database session

    Returns:
        OpenChestResult: Rewards from the chest

    Raises:
        HTTPException: If chest not found, already opened, or doesn't belong to user
    """
    # Get chest
    chest = db.query(LootChest).filter(LootChest.id == chest_id).first()

    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loot chest not found"
        )

    if chest.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This chest doesn't belong to you"
        )

    if chest.is_opened:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This chest has already been opened"
        )

    # Open chest
    try:
        result = GameEngine.open_loot_chest(chest, current_user, db)

        # Check for new achievements
        new_achievements = GameEngine.check_and_award_achievements(current_user, db)

        return OpenChestResult(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== DAILY STREAK ENDPOINTS ====================

@router.get("/streak", response_model=StreakResponse)
def get_streak_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's streak information

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        StreakResponse: Streak information
    """
    streak = db.query(DailyStreak).filter(DailyStreak.user_id == current_user.id).first()

    if not streak:
        # Create new streak record
        streak = DailyStreak(user_id=current_user.id)
        db.add(streak)
        db.commit()
        db.refresh(streak)

    return StreakResponse.model_validate(streak)


@router.post("/streak/checkin", response_model=CheckInResult)
def daily_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform daily check-in to maintain streak

    Awards bonus XP for consecutive days

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        CheckInResult: Check-in result with rewards
    """
    result = GameEngine.process_daily_checkin(current_user, db)

    # Check for new achievements
    new_achievements = GameEngine.check_and_award_achievements(current_user, db)

    if new_achievements:
        result["new_achievements"] = [
            {
                "name": a.name,
                "description": a.description,
                "icon": a.icon
            }
            for a in new_achievements
        ]

    return CheckInResult(**result)


# ==================== ACHIEVEMENT ENDPOINTS ====================

@router.get("/achievements", response_model=List[AchievementProgressResponse])
def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all achievements with user progress

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[AchievementProgressResponse]: All achievements with progress
    """
    # Get all achievements
    all_achievements = db.query(Achievement).order_by(Achievement.order, Achievement.id).all()

    # Get user's unlocked achievements
    unlocked = {
        ua.achievement_id: ua.unlocked_at
        for ua in db.query(UserAchievement).filter(
            UserAchievement.user_id == current_user.id
        ).all()
    }

    # Get user stats for progress calculation
    stats = GameEngine.get_user_stats(current_user, db)

    # Build response
    result = []
    for achievement in all_achievements:
        is_unlocked = achievement.id in unlocked

        # Calculate progress
        if achievement.achievement_type.value == "challenge_count":
            progress = stats.get("challenges_completed", 0)
        elif achievement.achievement_type.value == "xp_total":
            progress = stats.get("total_xp", 0)
        elif achievement.achievement_type.value == "level_reached":
            progress = stats.get("level", 0)
        elif achievement.achievement_type.value == "streak_count":
            progress = stats.get("current_streak", 0)
        elif achievement.achievement_type.value == "perfect_score":
            progress = stats.get("perfect_scores", 0)
        elif achievement.achievement_type.value == "loot_collector":
            progress = stats.get("chests_opened", 0)
        else:
            progress = 0

        result.append(achievement.to_dict(unlocked=is_unlocked, progress=progress))

    return [AchievementProgressResponse(**item) for item in result]


@router.get("/achievements/unlocked", response_model=List[UserAchievementResponse])
def get_unlocked_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all achievements unlocked by current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list[UserAchievementResponse]: Unlocked achievements
    """
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id
    ).order_by(UserAchievement.unlocked_at.desc()).all()

    result = []
    for ua in user_achievements:
        achievement = ua.achievement
        result.append(UserAchievementResponse(
            id=ua.id,
            achievement_id=achievement.id,
            achievement_name=achievement.name,
            achievement_description=achievement.description,
            achievement_icon=achievement.icon,
            unlocked_at=ua.unlocked_at
        ))

    return result


@router.post("/achievements/check")
def check_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger achievement check (usually done automatically)

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Newly unlocked achievements
    """
    new_achievements = GameEngine.check_and_award_achievements(current_user, db)

    return {
        "newly_unlocked": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "xp_reward": a.xp_reward
            }
            for a in new_achievements
        ],
        "count": len(new_achievements)
    }


# ==================== GAME STATS ENDPOINT ====================

@router.get("/stats", response_model=GameStatsResponse)
def get_game_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive game statistics for current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        GameStatsResponse: Complete game statistics
    """
    stats = GameEngine.get_user_stats(current_user, db)

    # Count unopened chests
    unopened_chests = db.query(LootChest).filter(
        LootChest.user_id == current_user.id,
        LootChest.is_opened == False
    ).count()

    # Count achievements
    unlocked_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id
    ).count()

    total_achievements = db.query(Achievement).count()

    # Calculate XP for next level
    xp_for_next = GameEngine.xp_for_next_level(current_user.xp)

    return GameStatsResponse(
        user_id=current_user.id,
        username=current_user.username,
        level=current_user.level,
        xp=current_user.xp,
        xp_for_next_level=xp_for_next,
        challenges_completed=stats["challenges_completed"],
        perfect_scores=stats["perfect_scores"],
        current_streak=stats["current_streak"],
        longest_streak=stats["longest_streak"],
        unopened_chests=unopened_chests,
        opened_chests=stats["chests_opened"],
        achievements_unlocked=unlocked_achievements,
        total_achievements=total_achievements
    )
