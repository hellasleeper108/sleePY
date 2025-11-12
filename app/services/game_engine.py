"""
Game Engine - Core RPG mechanics for PyQuest

Handles all XP calculations, loot generation, streak tracking, and achievement unlocking
"""
import random
from datetime import date, datetime
from typing import Optional, Tuple, List, Dict
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.challenge import Challenge, DifficultyLevel
from app.models.progress import Progress
from app.models.loot_chest import LootChest, ChestRarity
from app.models.daily_streak import DailyStreak
from app.models.achievement import Achievement, AchievementType
from app.models.user_achievement import UserAchievement


class GameEngine:
    """
    Core game engine for PyQuest RPG mechanics

    Manages XP, levels, loot, streaks, and achievements
    """

    @staticmethod
    def calculate_xp_for_challenge(challenge: Challenge) -> int:
        """
        Calculate XP reward for a challenge based on difficulty

        Args:
            challenge: Challenge object

        Returns:
            int: XP reward amount
        """
        base_xp = challenge.xp_reward

        # Apply difficulty multipliers
        multipliers = {
            DifficultyLevel.BEGINNER: 1.0,
            DifficultyLevel.INTERMEDIATE: 1.5,
            DifficultyLevel.ADVANCED: 2.0,
            DifficultyLevel.EXPERT: 3.0,
        }

        multiplier = multipliers.get(challenge.difficulty, 1.0)
        return int(base_xp * multiplier)

    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """
        Calculate level based on total XP

        Formula: level = floor(XP / 100)
        This is simpler than the original sqrt formula for clearer progression

        Level thresholds:
        - Level 1: 0-99 XP
        - Level 2: 100-199 XP
        - Level 3: 200-299 XP
        - Level 10: 900-999 XP
        - Level 100: 9900-9999 XP

        Args:
            xp: Total experience points

        Returns:
            int: Current level
        """
        return max(1, xp // 100 + 1)

    @staticmethod
    def xp_for_next_level(current_xp: int) -> int:
        """
        Calculate XP needed for next level

        Args:
            current_xp: Current total XP

        Returns:
            int: XP needed to reach next level
        """
        current_level = GameEngine.calculate_level_from_xp(current_xp)
        next_level_threshold = (current_level) * 100
        return next_level_threshold - current_xp

    @staticmethod
    def award_xp(user: User, amount: int, db: Session) -> Dict:
        """
        Award XP to user and handle level ups

        Args:
            user: User object
            amount: XP amount to award
            db: Database session

        Returns:
            dict: Result with level up info
        """
        old_level = user.level
        old_xp = user.xp

        user.xp += amount
        new_level = GameEngine.calculate_level_from_xp(user.xp)

        leveled_up = new_level > old_level
        if leveled_up:
            user.level = new_level

        result = {
            "xp_gained": amount,
            "total_xp": user.xp,
            "old_level": old_level,
            "new_level": new_level,
            "leveled_up": leveled_up,
            "levels_gained": new_level - old_level if leveled_up else 0
        }

        # Award loot chest on level up
        if leveled_up:
            chest = GameEngine.generate_loot_chest(user, db, reason=f"Level {new_level} reached!")
            result["level_up_chest"] = {
                "rarity": chest.rarity.value,
                "chest_id": chest.id
            }

        return result

    @staticmethod
    def generate_loot_chest(
        user: User,
        db: Session,
        rarity: Optional[ChestRarity] = None,
        reason: str = "Random drop"
    ) -> LootChest:
        """
        Generate a loot chest for the user

        Args:
            user: User to receive chest
            db: Database session
            rarity: Specific rarity (if None, randomly determined)
            reason: Why the chest was awarded

        Returns:
            LootChest: Created chest object
        """
        if rarity is None:
            rarity = GameEngine.roll_chest_rarity()

        chest = LootChest(
            user_id=user.id,
            rarity=rarity,
            xp_reward=0,  # Set when opened
            is_opened=False,
            earned_reason=reason
        )

        db.add(chest)
        db.commit()
        db.refresh(chest)

        return chest

    @staticmethod
    def roll_chest_rarity() -> ChestRarity:
        """
        Randomly determine chest rarity based on weights

        Returns:
            ChestRarity: Randomly selected rarity
        """
        weights = LootChest.get_rarity_weights()
        rarities = list(weights.keys())
        weight_values = list(weights.values())

        return random.choices(rarities, weights=weight_values, k=1)[0]

    @staticmethod
    def open_loot_chest(chest: LootChest, user: User, db: Session) -> Dict:
        """
        Open a loot chest and award rewards

        Args:
            chest: LootChest to open
            user: User opening the chest
            db: Database session

        Returns:
            dict: Rewards from the chest

        Raises:
            ValueError: If chest already opened or doesn't belong to user
        """
        if chest.is_opened:
            raise ValueError("Chest already opened")

        if chest.user_id != user.id:
            raise ValueError("Chest doesn't belong to this user")

        # Roll XP reward
        min_xp, max_xp = LootChest.get_xp_range(chest.rarity)
        xp_reward = random.randint(min_xp, max_xp)

        # Mark chest as opened
        chest.xp_reward = xp_reward
        chest.is_opened = True
        chest.opened_at = datetime.utcnow()

        # Award XP
        xp_result = GameEngine.award_xp(user, xp_reward, db)

        db.commit()

        return {
            "chest_id": chest.id,
            "rarity": chest.rarity.value,
            "xp_reward": xp_reward,
            **xp_result
        }

    @staticmethod
    def process_daily_checkin(user: User, db: Session) -> Dict:
        """
        Process daily check-in for streak tracking

        Args:
            user: User checking in
            db: Database session

        Returns:
            dict: Check-in result with streak info and rewards
        """
        # Get or create streak record
        streak = db.query(DailyStreak).filter(DailyStreak.user_id == user.id).first()

        if not streak:
            streak = DailyStreak(user_id=user.id)
            db.add(streak)

        # Process check-in
        result = streak.check_in()

        # Award bonus XP if streak continued
        if result.get("bonus_xp", 0) > 0:
            xp_result = GameEngine.award_xp(user, result["bonus_xp"], db)
            result["xp_result"] = xp_result

        # Check for streak milestones
        if result.get("streak_continued") and streak.is_milestone():
            milestone_reward = GameEngine.award_streak_milestone(user, streak, db)
            result["milestone_reward"] = milestone_reward

        db.commit()
        db.refresh(streak)

        return result

    @staticmethod
    def award_streak_milestone(user: User, streak: DailyStreak, db: Session) -> Dict:
        """
        Award special rewards for reaching streak milestones

        Args:
            user: User who reached milestone
            streak: DailyStreak object
            db: Database session

        Returns:
            dict: Milestone rewards
        """
        current_streak = streak.current_streak

        # Determine chest rarity based on milestone
        if current_streak >= 365:
            rarity = ChestRarity.LEGENDARY
        elif current_streak >= 100:
            rarity = ChestRarity.EPIC
        elif current_streak >= 30:
            rarity = ChestRarity.RARE
        else:
            rarity = ChestRarity.COMMON

        # Award milestone chest
        chest = GameEngine.generate_loot_chest(
            user, db,
            rarity=rarity,
            reason=f"{current_streak} day streak milestone!"
        )

        # Bonus XP
        bonus_xp = current_streak * 2
        xp_result = GameEngine.award_xp(user, bonus_xp, db)

        return {
            "milestone": current_streak,
            "chest": {
                "id": chest.id,
                "rarity": chest.rarity.value
            },
            "bonus_xp": bonus_xp,
            "xp_result": xp_result
        }

    @staticmethod
    def check_and_award_achievements(user: User, db: Session) -> List[Achievement]:
        """
        Check and automatically award achievements user has earned

        Args:
            user: User to check achievements for
            db: Database session

        Returns:
            list: Newly unlocked achievements
        """
        # Get user stats
        stats = GameEngine.get_user_stats(user, db)

        # Get all achievements
        all_achievements = db.query(Achievement).all()

        # Get already unlocked achievement IDs
        unlocked_ids = {
            ua.achievement_id
            for ua in db.query(UserAchievement).filter(
                UserAchievement.user_id == user.id
            ).all()
        }

        # Check each achievement
        newly_unlocked = []

        for achievement in all_achievements:
            # Skip if already unlocked
            if achievement.id in unlocked_ids:
                continue

            # Check if criteria met
            if achievement.check_unlock(stats):
                # Award achievement
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id
                )
                db.add(user_achievement)

                # Award XP reward
                if achievement.xp_reward > 0:
                    GameEngine.award_xp(user, achievement.xp_reward, db)

                # Award loot chest if specified
                if achievement.grants_loot_chest:
                    GameEngine.generate_loot_chest(
                        user, db,
                        reason=f"Achievement: {achievement.name}"
                    )

                newly_unlocked.append(achievement)

        if newly_unlocked:
            db.commit()

        return newly_unlocked

    @staticmethod
    def get_user_stats(user: User, db: Session) -> Dict:
        """
        Get comprehensive user statistics for achievement checking

        Args:
            user: User object
            db: Database session

        Returns:
            dict: User statistics
        """
        # Count completed challenges
        completed_challenges = db.query(Progress).filter(
            Progress.user_id == user.id,
            Progress.is_completed == True
        ).count()

        # Count perfect scores (completed on first attempt)
        perfect_scores = db.query(Progress).filter(
            Progress.user_id == user.id,
            Progress.is_completed == True,
            Progress.attempts == 1
        ).count()

        # Count opened chests
        opened_chests = db.query(LootChest).filter(
            LootChest.user_id == user.id,
            LootChest.is_opened == True
        ).count()

        # Get streak info
        streak = db.query(DailyStreak).filter(DailyStreak.user_id == user.id).first()
        current_streak = streak.current_streak if streak else 0
        longest_streak = streak.longest_streak if streak else 0

        # Category completion (TODO: implement when needed)
        category_completion = {}

        return {
            "total_xp": user.xp,
            "level": user.level,
            "challenges_completed": completed_challenges,
            "perfect_scores": perfect_scores,
            "chests_opened": opened_chests,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "category_completion": category_completion
        }

    @staticmethod
    def roll_random_chest_drop(completion_count: int = 0) -> bool:
        """
        Determine if user gets a random chest drop

        Drop rate increases with challenges completed

        Args:
            completion_count: Number of challenges completed

        Returns:
            bool: True if chest should be dropped
        """
        # Base drop rate: 20%
        # Increases by 2% per challenge, max 50%
        drop_rate = min(0.20 + (completion_count * 0.02), 0.50)

        return random.random() < drop_rate


# Test and simulation functions
class GameSimulator:
    """
    Test functions to simulate game progression
    """

    @staticmethod
    def simulate_user_progression(
        db: Session,
        username: str = "test_user",
        days: int = 7,
        challenges_per_day: int = 3
    ) -> Dict:
        """
        Simulate a user's progression over multiple days

        Args:
            db: Database session
            username: Username to simulate
            days: Number of days to simulate
            challenges_per_day: Challenges completed per day

        Returns:
            dict: Simulation results
        """
        from app.models.user import User
        from app.models.challenge import Challenge

        # Get or create test user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            from app.core.security import get_password_hash
            user = User(
                username=username,
                email=f"{username}@test.com",
                hashed_password=get_password_hash("test123"),
                full_name="Test User"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Get some challenges
        challenges = db.query(Challenge).filter(Challenge.is_active == True).limit(10).all()
        if not challenges:
            print("No challenges found. Please run init_sample_data.py first")
            return {}

        results = {
            "username": username,
            "days_simulated": days,
            "daily_results": []
        }

        print(f"\n🎮 Simulating {days} days of gameplay for {username}...")
        print("=" * 60)

        for day in range(1, days + 1):
            print(f"\n📅 Day {day}")
            print("-" * 40)

            day_result = {
                "day": day,
                "activities": []
            }

            # Daily check-in
            checkin_result = GameEngine.process_daily_checkin(user, db)
            print(f"✅ Daily Check-in: {checkin_result['message']}")
            day_result["checkin"] = checkin_result

            # Complete challenges
            for i in range(challenges_per_day):
                challenge = random.choice(challenges)

                # Calculate XP
                xp_reward = GameEngine.calculate_xp_for_challenge(challenge)

                # Award XP
                xp_result = GameEngine.award_xp(user, xp_reward, db)

                print(f"🎯 Completed: {challenge.title} (+{xp_reward} XP)")

                if xp_result["leveled_up"]:
                    print(f"   🎉 LEVEL UP! {xp_result['old_level']} → {xp_result['new_level']}")

                # Random chest drop
                if GameEngine.roll_random_chest_drop(i):
                    chest = GameEngine.generate_loot_chest(user, db, reason="Random drop")
                    print(f"   📦 Loot chest dropped! ({chest.rarity.value})")
                    day_result["activities"].append({
                        "type": "chest_drop",
                        "rarity": chest.rarity.value
                    })

                day_result["activities"].append({
                    "type": "challenge_completed",
                    "challenge": challenge.title,
                    "xp": xp_reward,
                    "xp_result": xp_result
                })

            # Check achievements
            new_achievements = GameEngine.check_and_award_achievements(user, db)
            if new_achievements:
                print(f"\n🏆 New Achievements Unlocked:")
                for achievement in new_achievements:
                    print(f"   • {achievement.icon} {achievement.name}: {achievement.description}")
                day_result["new_achievements"] = [a.name for a in new_achievements]

            # Day summary
            print(f"\n📊 Day {day} Summary:")
            print(f"   Level: {user.level} | XP: {user.xp}")
            unopened_chests = db.query(LootChest).filter(
                LootChest.user_id == user.id,
                LootChest.is_opened == False
            ).count()
            print(f"   Unopened Chests: {unopened_chests}")

            results["daily_results"].append(day_result)

        # Final summary
        print("\n" + "=" * 60)
        print("🎊 SIMULATION COMPLETE!")
        print("=" * 60)

        stats = GameEngine.get_user_stats(user, db)
        print(f"\n📈 Final Stats:")
        print(f"   Level: {user.level}")
        print(f"   Total XP: {user.xp}")
        print(f"   Challenges Completed: {stats['challenges_completed']}")
        print(f"   Current Streak: {stats['current_streak']} days")
        print(f"   Longest Streak: {stats['longest_streak']} days")
        print(f"   Chests Opened: {stats['chests_opened']}")

        results["final_stats"] = stats

        return results

    @staticmethod
    def test_loot_system(db: Session, username: str = "test_user", num_chests: int = 10):
        """
        Test loot chest system by generating and opening chests

        Args:
            db: Database session
            username: Username to test with
            num_chests: Number of chests to generate and open
        """
        from app.models.user import User

        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User {username} not found")
            return

        print(f"\n🎲 Testing Loot System ({num_chests} chests)")
        print("=" * 60)

        total_xp = 0
        rarity_counts = {rarity: 0 for rarity in ChestRarity}

        for i in range(num_chests):
            # Generate chest
            chest = GameEngine.generate_loot_chest(user, db, reason="Test chest")
            rarity_counts[chest.rarity] += 1

            # Open chest
            result = GameEngine.open_loot_chest(chest, user, db)

            print(f"\n📦 Chest {i+1}: {result['rarity'].upper()}")
            print(f"   XP Reward: {result['xp_reward']}")

            if result.get('leveled_up'):
                print(f"   🎉 Level Up! {result['old_level']} → {result['new_level']}")

            total_xp += result['xp_reward']

        print("\n" + "=" * 60)
        print("📊 Loot Statistics:")
        print(f"   Total XP Gained: {total_xp}")
        print(f"   Average XP per Chest: {total_xp / num_chests:.1f}")
        print("\n   Rarity Distribution:")
        for rarity, count in rarity_counts.items():
            percentage = (count / num_chests) * 100
            print(f"      {rarity.value}: {count} ({percentage:.1f}%)")
