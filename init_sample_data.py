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
from app.models.learning_path import LearningPath, PathDifficulty, PathTopic
from app.models.lesson import Lesson, LessonType
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


def create_sample_learning_paths():
    """Create 5 sample learning paths with lessons"""
    db = SessionLocal()

    # Check if paths already exist
    existing = db.query(LearningPath).first()
    if existing:
        print("Learning paths already exist")
        return

    print("\nCreating learning paths...")

    # Path 1: Python Variables & Data Types
    path1 = LearningPath(
        title="Python Variables & Data Types",
        description="Master the fundamentals of Python variables and basic data types",
        topic=PathTopic.VARIABLES,
        difficulty=PathDifficulty.BEGINNER,
        estimated_hours=2,
        xp_reward=150,
        required_level=1,
        order=1
    )
    db.add(path1)
    db.flush()

    lessons_path1 = [
        Lesson(
            path_id=path1.id,
            title="Introduction to Variables",
            content="""# Introduction to Variables

Variables are containers for storing data values. In Python, you don't need to declare the type of a variable.

## Creating Variables

```python
# String variable
name = "PyQuest"

# Integer variable
level = 1

# Float variable
xp = 100.5

# Boolean variable
is_active = True
```

## Variable Naming Rules

- Must start with a letter or underscore
- Can only contain alphanumeric characters and underscores
- Case-sensitive (`name` and `Name` are different)
- Cannot be a Python keyword

## Try it yourself!

Create variables for your own game character.
""",
            lesson_type=LessonType.TUTORIAL,
            order=1,
            estimated_minutes=10,
            xp_reward=15
        ),
        Lesson(
            path_id=path1.id,
            title="Numbers in Python",
            content="""# Numbers in Python

Python has three numeric types: `int`, `float`, and `complex`.

## Integer (int)
Whole numbers, positive or negative.

```python
level = 5
score = -10
big_number = 1000000
```

## Float
Numbers with decimal points.

```python
pi = 3.14159
temperature = 98.6
xp_multiplier = 1.5
```

## Arithmetic Operations

```python
# Addition
total = 10 + 5  # 15

# Subtraction
difference = 10 - 5  # 5

# Multiplication
product = 10 * 5  # 50

# Division
quotient = 10 / 5  # 2.0

# Floor division
floor_div = 10 // 3  # 3

# Modulus (remainder)
remainder = 10 % 3  # 1

# Exponentiation
power = 2 ** 3  # 8
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=2,
            estimated_minutes=15,
            xp_reward=20
        ),
        Lesson(
            path_id=path1.id,
            title="Strings and Text",
            content="""# Strings in Python

Strings are sequences of characters enclosed in quotes.

## Creating Strings

```python
# Single quotes
greeting = 'Hello'

# Double quotes
name = "PyQuest"

# Multi-line strings
description = '''This is a
multi-line string
in Python'''
```

## String Operations

```python
# Concatenation
full_name = "John" + " " + "Doe"

# Repetition
repeated = "Ha" * 3  # "HaHaHa"

# Length
length = len("Hello")  # 5

# Indexing
first_char = "Python"[0]  # 'P'

# Slicing
substring = "Python"[0:3]  # 'Pyt'
```

## String Methods

```python
text = "hello world"

# Uppercase
text.upper()  # "HELLO WORLD"

# Lowercase
text.lower()  # "hello world"

# Title case
text.title()  # "Hello World"

# Replace
text.replace("world", "Python")  # "hello Python"

# Split
words = text.split()  # ['hello', 'world']
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=3,
            estimated_minutes=15,
            xp_reward=20
        )
    ]

    for lesson in lessons_path1:
        db.add(lesson)

    # Path 2: Control Flow
    path2 = LearningPath(
        title="Control Flow: If, Elif, Else",
        description="Learn to control program flow with conditional statements",
        topic=PathTopic.CONTROL_FLOW,
        difficulty=PathDifficulty.BEGINNER,
        estimated_hours=3,
        xp_reward=200,
        required_level=1,
        order=2
    )
    db.add(path2)
    db.flush()

    lessons_path2 = [
        Lesson(
            path_id=path2.id,
            title="If Statements",
            content="""# If Statements

Control the flow of your program based on conditions.

## Basic If Statement

```python
level = 5

if level >= 5:
    print("You can access advanced challenges!")
```

## Comparison Operators

- `==` Equal to
- `!=` Not equal to
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal to
- `<=` Less than or equal to

```python
xp = 100

if xp >= 100:
    print("Level up!")

if xp == 100:
    print("Exactly 100 XP")

if xp != 0:
    print("You have some XP")
```

## Logical Operators

```python
level = 5
xp = 150

# AND - both conditions must be True
if level >= 5 and xp >= 100:
    print("Requirements met!")

# OR - at least one condition must be True
if level >= 10 or xp >= 500:
    print("Advanced user!")

# NOT - inverse the condition
if not level == 1:
    print("Not a beginner")
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=1,
            estimated_minutes=15,
            xp_reward=25
        ),
        Lesson(
            path_id=path2.id,
            title="Elif and Else",
            content="""# Elif and Else

Handle multiple conditions and default cases.

## Elif (Else If)

```python
level = 5

if level >= 10:
    print("Expert")
elif level >= 5:
    print("Intermediate")
elif level >= 1:
    print("Beginner")
```

## Else (Default Case)

```python
score = 75

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Your grade is: {grade}")
```

## Nested If Statements

```python
has_key = True
level = 5

if has_key:
    if level >= 5:
        print("You can enter the boss room!")
    else:
        print("Level too low")
else:
    print("You need a key")
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=2,
            estimated_minutes=15,
            xp_reward=25
        )
    ]

    for lesson in lessons_path2:
        db.add(lesson)

    # Path 3: Loops
    path3 = LearningPath(
        title="Loops: For and While",
        description="Master iteration with for and while loops",
        topic=PathTopic.CONTROL_FLOW,
        difficulty=PathDifficulty.BEGINNER,
        estimated_hours=3,
        xp_reward=200,
        required_level=2,
        order=3
    )
    db.add(path3)
    db.flush()

    lessons_path3 = [
        Lesson(
            path_id=path3.id,
            title="For Loops",
            content="""# For Loops

Iterate over sequences like lists, strings, and ranges.

## Basic For Loop with Range

```python
# Print numbers 0 to 4
for i in range(5):
    print(i)

# Range with start and end
for i in range(1, 6):  # 1 to 5
    print(i)

# Range with step
for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
    print(i)
```

## Looping Over Lists

```python
challenges = ["Variables", "Loops", "Functions"]

for challenge in challenges:
    print(f"Complete: {challenge}")
```

## Looping Over Strings

```python
word = "Python"

for letter in word:
    print(letter)
```

## Break and Continue

```python
# Break - exit loop early
for i in range(10):
    if i == 5:
        break
    print(i)  # Prints 0-4

# Continue - skip current iteration
for i in range(5):
    if i == 2:
        continue
    print(i)  # Prints 0, 1, 3, 4
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=1,
            estimated_minutes=20,
            xp_reward=30
        ),
        Lesson(
            path_id=path3.id,
            title="While Loops",
            content="""# While Loops

Repeat code while a condition is true.

## Basic While Loop

```python
count = 0

while count < 5:
    print(count)
    count += 1
```

## Game Example

```python
health = 100
damage = 20

while health > 0:
    health -= damage
    print(f"Health: {health}")

print("Game Over!")
```

## While with Break

```python
while True:
    user_input = input("Enter 'quit' to exit: ")
    if user_input == "quit":
        break
    print(f"You entered: {user_input}")
```

## Infinite Loop Warning

```python
# Be careful! This loops forever
# while True:
#     print("This never stops!")

# Always have an exit condition
attempts = 0
while attempts < 3:
    print(f"Attempt {attempts + 1}")
    attempts += 1
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=2,
            estimated_minutes=20,
            xp_reward=30
        )
    ]

    for lesson in lessons_path3:
        db.add(lesson)

    # Path 4: Functions
    path4 = LearningPath(
        title="Functions in Python",
        description="Create reusable code with functions",
        topic=PathTopic.FUNCTIONS,
        difficulty=PathDifficulty.INTERMEDIATE,
        estimated_hours=4,
        xp_reward=250,
        required_level=3,
        order=4
    )
    db.add(path4)
    db.flush()

    lessons_path4 = [
        Lesson(
            path_id=path4.id,
            title="Defining Functions",
            content="""# Defining Functions

Functions are reusable blocks of code.

## Basic Function

```python
def greet():
    print("Hello, PyQuest!")

# Call the function
greet()
```

## Functions with Parameters

```python
def greet_user(name):
    print(f"Hello, {name}!")

greet_user("Alice")  # Hello, Alice!
greet_user("Bob")    # Hello, Bob!
```

## Multiple Parameters

```python
def calculate_xp(challenges, difficulty):
    base_xp = challenges * 10
    if difficulty == "hard":
        return base_xp * 2
    return base_xp

xp = calculate_xp(5, "hard")
print(xp)  # 100
```

## Default Parameters

```python
def power_up(health, amount=10):
    return health + amount

print(power_up(50))      # 60
print(power_up(50, 25))  # 75
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=1,
            estimated_minutes=20,
            xp_reward=35
        ),
        Lesson(
            path_id=path4.id,
            title="Return Values",
            content="""# Return Values

Functions can return values to be used elsewhere.

## Basic Return

```python
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)  # 8
```

## Multiple Return Values

```python
def get_user_stats(user):
    level = 5
    xp = 100
    return level, xp

lvl, experience = get_user_stats("Alice")
print(f"Level: {lvl}, XP: {experience}")
```

## Conditional Returns

```python
def check_level(xp):
    if xp >= 1000:
        return "Expert"
    elif xp >= 500:
        return "Intermediate"
    else:
        return "Beginner"

status = check_level(750)
print(status)  # Intermediate
```

## Return vs Print

```python
# Print - displays output
def show_message():
    print("Hello")

# Return - gives back a value
def get_message():
    return "Hello"

# show_message() can't be stored
# msg = show_message()  # msg is None

# get_message() returns a value
msg = get_message()
print(msg)  # Hello
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=2,
            estimated_minutes=20,
            xp_reward=35
        )
    ]

    for lesson in lessons_path4:
        db.add(lesson)

    # Path 5: Object-Oriented Programming
    path5 = LearningPath(
        title="Introduction to OOP",
        description="Learn object-oriented programming with classes and objects",
        topic=PathTopic.OOP,
        difficulty=PathDifficulty.ADVANCED,
        estimated_hours=5,
        xp_reward=300,
        required_level=5,
        order=5
    )
    db.add(path5)
    db.flush()

    lessons_path5 = [
        Lesson(
            path_id=path5.id,
            title="Classes and Objects",
            content="""# Classes and Objects

Object-Oriented Programming (OOP) organizes code into objects.

## What are Classes?

A class is a blueprint for creating objects.

```python
class Player:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.xp = 0

    def gain_xp(self, amount):
        self.xp += amount
        print(f"{self.name} gained {amount} XP!")

# Create objects (instances)
player1 = Player("Alice", 1)
player2 = Player("Bob", 1)

# Use methods
player1.gain_xp(50)  # Alice gained 50 XP!
print(player1.xp)    # 50
```

## The __init__ Method

The `__init__` method is called when creating a new object.

```python
class Character:
    def __init__(self, name, health=100):
        self.name = name
        self.health = health
        print(f"{name} created with {health} health!")

hero = Character("Hero")  # Hero created with 100 health!
```

## Instance vs Class Variables

```python
class Game:
    # Class variable (shared by all instances)
    total_players = 0

    def __init__(self, player_name):
        # Instance variable (unique to each object)
        self.player = player_name
        Game.total_players += 1

game1 = Game("Alice")
game2 = Game("Bob")
print(Game.total_players)  # 2
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=1,
            estimated_minutes=25,
            xp_reward=40
        ),
        Lesson(
            path_id=path5.id,
            title="Methods and Properties",
            content="""# Methods and Properties

Methods are functions that belong to a class.

## Instance Methods

```python
class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)
        return f"Added {item}"

    def show_items(self):
        if not self.items:
            return "Inventory is empty"
        return f"Items: {', '.join(self.items)}"

inv = Inventory()
inv.add_item("Sword")
inv.add_item("Shield")
print(inv.show_items())  # Items: Sword, Shield
```

## Properties with @property

```python
class Player:
    def __init__(self, name):
        self.name = name
        self._xp = 0

    @property
    def level(self):
        return self._xp // 100 + 1

    def gain_xp(self, amount):
        self._xp += amount

player = Player("Alice")
print(player.level)      # 1
player.gain_xp(250)
print(player.level)      # 3
```

## String Representation

```python
class Quest:
    def __init__(self, title, xp_reward):
        self.title = title
        self.xp_reward = xp_reward

    def __str__(self):
        return f"Quest: {self.title} ({self.xp_reward} XP)"

    def __repr__(self):
        return f"Quest('{self.title}', {self.xp_reward})"

quest = Quest("Dragon Slayer", 500)
print(quest)       # Quest: Dragon Slayer (500 XP)
print(repr(quest)) # Quest('Dragon Slayer', 500)
```
""",
            lesson_type=LessonType.TUTORIAL,
            order=2,
            estimated_minutes=25,
            xp_reward=40
        )
    ]

    for lesson in lessons_path5:
        db.add(lesson)

    db.commit()
    print(f"✓ Created 5 learning paths with {len(lessons_path1) + len(lessons_path2) + len(lessons_path3) + len(lessons_path4) + len(lessons_path5)} lessons")
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
    create_sample_learning_paths()

    print("\n✓ Sample data initialization complete!")
    print("\nYou can now:")
    print("1. Start the server: uvicorn main:app --reload")
    print("2. Visit the API docs: http://localhost:8000/docs")
    print("3. Login with admin credentials (username: admin, password: admin123)")
    print("4. Or create a new user account via /api/auth/signup")


if __name__ == "__main__":
    main()
