"""
Sample data initialization script

Run this script to populate your database with sample challenges and badges:
    python init_sample_data.py
"""
from app.db.session import SessionLocal, init_db
from app.models.user import User
from app.models.challenge import Challenge, DifficultyLevel, ChallengeCategory
from app.models.badge import Badge
from app.models.achievement import Achievement, AchievementType
from app.core.security import get_password_hash


def create_sample_admin():
    """Create a sample admin user"""
    db = SessionLocal()

    # Check if admin already exists
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("Admin user already exists")
        return

    admin = User(
        username="admin",
        email="admin@pyquest.com",
        full_name="Admin User",
        hashed_password=get_password_hash("admin123"),
        xp=1000,
        level=5,
        is_active=True,
        is_superuser=True
    )

    db.add(admin)
    db.commit()
    print("✓ Created admin user (username: admin, password: admin123)")
    db.close()


def create_sample_challenges():
    """Create sample coding challenges"""
    db = SessionLocal()

    # Check if challenges already exist
    existing = db.query(Challenge).first()
    if existing:
        print("Challenges already exist")
        return

    challenges = [
        Challenge(
            title="Hello World",
            description="Write your first Python function!",
            instructions="Create a function called 'hello_world' that returns the string 'Hello World'.",
            difficulty=DifficultyLevel.BEGINNER,
            category=ChallengeCategory.BASICS,
            starter_code="def hello_world():\n    # Your code here\n    pass",
            solution="def hello_world():\n    return 'Hello World'",
            test_cases='[{"input": [], "expected": "Hello World"}]',
            xp_reward=10,
            required_level=1,
            order=1,
            is_active=True
        ),
        Challenge(
            title="Sum Two Numbers",
            description="Learn how to work with function parameters",
            instructions="Create a function called 'add_numbers' that takes two parameters and returns their sum.",
            difficulty=DifficultyLevel.BEGINNER,
            category=ChallengeCategory.BASICS,
            starter_code="def add_numbers(a, b):\n    # Your code here\n    pass",
            solution="def add_numbers(a, b):\n    return a + b",
            test_cases='[{"input": [2, 3], "expected": 5}, {"input": [10, 20], "expected": 30}]',
            xp_reward=10,
            required_level=1,
            order=2,
            is_active=True
        ),
        Challenge(
            title="Find Maximum",
            description="Work with lists and comparisons",
            instructions="Create a function called 'find_max' that takes a list of numbers and returns the largest one.",
            difficulty=DifficultyLevel.BEGINNER,
            category=ChallengeCategory.BASICS,
            starter_code="def find_max(numbers):\n    # Your code here\n    pass",
            solution="def find_max(numbers):\n    return max(numbers)",
            test_cases='[{"input": [[1, 5, 3, 9, 2]], "expected": 9}]',
            xp_reward=15,
            required_level=1,
            order=3,
            is_active=True
        ),
        Challenge(
            title="Count Vowels",
            description="String manipulation challenge",
            instructions="Create a function 'count_vowels' that counts the number of vowels (a,e,i,o,u) in a string.",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=ChallengeCategory.BASICS,
            starter_code="def count_vowels(text):\n    # Your code here\n    pass",
            solution="def count_vowels(text):\n    vowels = 'aeiouAEIOU'\n    return sum(1 for char in text if char in vowels)",
            test_cases='[{"input": ["hello"], "expected": 2}, {"input": ["Python"], "expected": 1}]',
            xp_reward=20,
            required_level=2,
            order=4,
            is_active=True
        ),
        Challenge(
            title="Reverse a List",
            description="Learn about list manipulation",
            instructions="Create a function 'reverse_list' that reverses a list without using the built-in reverse().",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=ChallengeCategory.DATA_STRUCTURES,
            starter_code="def reverse_list(items):\n    # Your code here\n    pass",
            solution="def reverse_list(items):\n    return items[::-1]",
            test_cases='[{"input": [[1, 2, 3, 4]], "expected": [4, 3, 2, 1]}]',
            xp_reward=20,
            required_level=2,
            order=5,
            is_active=True
        ),
        Challenge(
            title="FizzBuzz",
            description="Classic programming challenge",
            instructions="Create a function 'fizzbuzz' that returns a list of strings from 1 to n. For multiples of 3, use 'Fizz'. For multiples of 5, use 'Buzz'. For multiples of both, use 'FizzBuzz'.",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=ChallengeCategory.ALGORITHMS,
            starter_code="def fizzbuzz(n):\n    # Your code here\n    pass",
            solution="def fizzbuzz(n):\n    result = []\n    for i in range(1, n + 1):\n        if i % 15 == 0:\n            result.append('FizzBuzz')\n        elif i % 3 == 0:\n            result.append('Fizz')\n        elif i % 5 == 0:\n            result.append('Buzz')\n        else:\n            result.append(str(i))\n    return result",
            test_cases='[{"input": [15], "expected": ["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]}]',
            xp_reward=25,
            required_level=2,
            order=6,
            is_active=True
        ),
        Challenge(
            title="Palindrome Checker",
            description="String algorithms",
            instructions="Create a function 'is_palindrome' that checks if a string is a palindrome (reads the same forwards and backwards).",
            difficulty=DifficultyLevel.ADVANCED,
            category=ChallengeCategory.ALGORITHMS,
            starter_code="def is_palindrome(text):\n    # Your code here\n    pass",
            solution="def is_palindrome(text):\n    text = text.lower().replace(' ', '')\n    return text == text[::-1]",
            test_cases='[{"input": ["racecar"], "expected": true}, {"input": ["hello"], "expected": false}]',
            xp_reward=30,
            required_level=3,
            order=7,
            is_active=True
        ),
        Challenge(
            title="Binary Search",
            description="Implement a classic search algorithm",
            instructions="Create a function 'binary_search' that searches for a target in a sorted list using binary search. Return the index or -1 if not found.",
            difficulty=DifficultyLevel.ADVANCED,
            category=ChallengeCategory.ALGORITHMS,
            starter_code="def binary_search(arr, target):\n    # Your code here\n    pass",
            solution="def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
            test_cases='[{"input": [[1,2,3,4,5,6,7,8,9], 5], "expected": 4}]',
            xp_reward=35,
            required_level=3,
            order=8,
            is_active=True
        ),
    ]

    for challenge in challenges:
        db.add(challenge)

    db.commit()
    print(f"✓ Created {len(challenges)} sample challenges")
    db.close()


def create_sample_badges():
    """Create sample badges"""
    db = SessionLocal()

    # Check if badges already exist
    existing = db.query(Badge).first()
    if existing:
        print("Badges already exist")
        return

    badges = [
        Badge(
            name="First Steps",
            description="Complete your first challenge",
            icon="🎯",
            criteria="Complete any challenge"
        ),
        Badge(
            name="Quick Learner",
            description="Complete 5 challenges",
            icon="⚡",
            criteria="Complete 5 challenges"
        ),
        Badge(
            name="Python Novice",
            description="Reach level 2",
            icon="🐍",
            criteria="Reach level 2"
        ),
        Badge(
            name="Coding Streak",
            description="Complete challenges 3 days in a row",
            icon="🔥",
            criteria="3 day streak"
        ),
        Badge(
            name="Algorithm Master",
            description="Complete all algorithm challenges",
            icon="🧠",
            criteria="Complete all challenges in Algorithms category"
        ),
        Badge(
            name="Perfect Score",
            description="Complete a challenge on first try",
            icon="💯",
            criteria="Complete a challenge with only 1 attempt"
        ),
        Badge(
            name="Python Expert",
            description="Reach level 5",
            icon="🏆",
            criteria="Reach level 5"
        ),
    ]

    for badge in badges:
        db.add(badge)

    db.commit()
    print(f"✓ Created {len(badges)} sample badges")
    db.close()


def create_sample_achievements():
    """Create sample achievements with auto-unlock criteria"""
    db = SessionLocal()

    # Check if achievements already exist
    existing = db.query(Achievement).first()
    if existing:
        print("Achievements already exist")
        return

    achievements = [
        # Challenge completion achievements
        Achievement(
            name="First Steps",
            description="Complete your first challenge",
            icon="🎯",
            achievement_type=AchievementType.CHALLENGE_COUNT,
            criteria_value=1,
            xp_reward=50,
            grants_loot_chest=True,
            is_secret=False,
            order=1
        ),
        Achievement(
            name="Getting Started",
            description="Complete 5 challenges",
            icon="⭐",
            achievement_type=AchievementType.CHALLENGE_COUNT,
            criteria_value=5,
            xp_reward=100,
            grants_loot_chest=True,
            is_secret=False,
            order=2
        ),
        Achievement(
            name="Dedicated Learner",
            description="Complete 10 challenges",
            icon="📚",
            achievement_type=AchievementType.CHALLENGE_COUNT,
            criteria_value=10,
            xp_reward=200,
            grants_loot_chest=True,
            is_secret=False,
            order=3
        ),
        Achievement(
            name="Challenge Master",
            description="Complete 25 challenges",
            icon="🏆",
            achievement_type=AchievementType.CHALLENGE_COUNT,
            criteria_value=25,
            xp_reward=500,
            grants_loot_chest=True,
            is_secret=False,
            order=4
        ),

        # Level achievements
        Achievement(
            name="Level Up!",
            description="Reach level 2",
            icon="🌟",
            achievement_type=AchievementType.LEVEL_REACHED,
            criteria_value=2,
            xp_reward=50,
            grants_loot_chest=False,
            is_secret=False,
            order=10
        ),
        Achievement(
            name="Rising Star",
            description="Reach level 5",
            icon="💫",
            achievement_type=AchievementType.LEVEL_REACHED,
            criteria_value=5,
            xp_reward=100,
            grants_loot_chest=True,
            is_secret=False,
            order=11
        ),
        Achievement(
            name="Python Pro",
            description="Reach level 10",
            icon="🐍",
            achievement_type=AchievementType.LEVEL_REACHED,
            criteria_value=10,
            xp_reward=250,
            grants_loot_chest=True,
            is_secret=False,
            order=12
        ),

        # Streak achievements
        Achievement(
            name="Commitment",
            description="Maintain a 3-day streak",
            icon="🔥",
            achievement_type=AchievementType.STREAK_COUNT,
            criteria_value=3,
            xp_reward=75,
            grants_loot_chest=False,
            is_secret=False,
            order=20
        ),
        Achievement(
            name="Week Warrior",
            description="Maintain a 7-day streak",
            icon="⚡",
            achievement_type=AchievementType.STREAK_COUNT,
            criteria_value=7,
            xp_reward=150,
            grants_loot_chest=True,
            is_secret=False,
            order=21
        ),
        Achievement(
            name="Unstoppable",
            description="Maintain a 30-day streak",
            icon="🌟",
            achievement_type=AchievementType.STREAK_COUNT,
            criteria_value=30,
            xp_reward=500,
            grants_loot_chest=True,
            is_secret=False,
            order=22
        ),

        # Perfect score achievements
        Achievement(
            name="First Try!",
            description="Complete a challenge on your first attempt",
            icon="💯",
            achievement_type=AchievementType.PERFECT_SCORE,
            criteria_value=1,
            xp_reward=100,
            grants_loot_chest=False,
            is_secret=False,
            order=30
        ),
        Achievement(
            name="Perfectionist",
            description="Complete 5 challenges on first attempt",
            icon="✨",
            achievement_type=AchievementType.PERFECT_SCORE,
            criteria_value=5,
            xp_reward=250,
            grants_loot_chest=True,
            is_secret=False,
            order=31
        ),

        # Loot collector achievements
        Achievement(
            name="Treasure Hunter",
            description="Open 10 loot chests",
            icon="📦",
            achievement_type=AchievementType.LOOT_COLLECTOR,
            criteria_value=10,
            xp_reward=100,
            grants_loot_chest=False,
            is_secret=False,
            order=40
        ),
        Achievement(
            name="Hoarder",
            description="Open 50 loot chests",
            icon="💎",
            achievement_type=AchievementType.LOOT_COLLECTOR,
            criteria_value=50,
            xp_reward=300,
            grants_loot_chest=True,
            is_secret=False,
            order=41
        ),

        # XP achievements
        Achievement(
            name="XP Collector",
            description="Earn 1000 total XP",
            icon="💰",
            achievement_type=AchievementType.XP_TOTAL,
            criteria_value=1000,
            xp_reward=100,
            grants_loot_chest=False,
            is_secret=False,
            order=50
        ),
        Achievement(
            name="XP Master",
            description="Earn 5000 total XP",
            icon="👑",
            achievement_type=AchievementType.XP_TOTAL,
            criteria_value=5000,
            xp_reward=500,
            grants_loot_chest=True,
            is_secret=False,
            order=51
        ),

        # Secret achievements
        Achievement(
            name="Secret Master",
            description="You've discovered a secret!",
            icon="🎁",
            achievement_type=AchievementType.CHALLENGE_COUNT,
            criteria_value=50,
            xp_reward=1000,
            grants_loot_chest=True,
            is_secret=True,
            order=100
        ),
    ]

    for achievement in achievements:
        db.add(achievement)

    db.commit()
    print(f"✓ Created {len(achievements)} sample achievements")
    db.close()


def main():
    """Main function to initialize sample data"""
    print("Initializing PyQuest database with sample data...\n")

    # Initialize database tables
    print("Creating database tables...")
    init_db()

    # Create sample data
    create_sample_admin()
    create_sample_challenges()
    create_sample_badges()
    create_sample_achievements()

    print("\n✓ Sample data initialization complete!")
    print("\nYou can now:")
    print("1. Start the server: uvicorn main:app --reload")
    print("2. Visit the API docs: http://localhost:8000/docs")
    print("3. Login with admin credentials (username: admin, password: admin123)")
    print("4. Or create a new user account via /api/auth/signup")


if __name__ == "__main__":
    main()
