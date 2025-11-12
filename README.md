# PyQuest - Gamified Python Learning Platform

A gamified learning platform where users complete coding challenges, earn XP, level up, and unlock new quests as they master core Python concepts.

## Features

- **User System**: Sign up/login with JWT authentication, XP tracking, levels, and badges
- **Challenge System**: Full CRUD operations for coding challenges with difficulty levels
- **Progress Tracking**: Track completed lessons and challenges per user
- **Gamification**: Experience points, levels, badges, and leaderboards
- **REST API**: Complete RESTful API with automatic documentation
- **Database**: SQLite for local dev, easily scalable to PostgreSQL

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type hints
- **JWT**: Secure authentication with JSON Web Tokens
- **Uvicorn**: ASGI server for running the application
- **SQLite/PostgreSQL**: Database (SQLite default, PostgreSQL for production)

## Project Structure

```
sleePY/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── users.py         # User management endpoints
│   │       ├── challenges.py    # Challenge CRUD endpoints
│   │       ├── progress.py      # Progress tracking endpoints
│   │       └── badges.py        # Badge system endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Application configuration
│   │   └── security.py          # Auth & security utilities
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py              # Database base class
│   │   └── session.py           # Database session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── challenge.py         # Challenge model
│   │   ├── progress.py          # Progress model
│   │   └── badge.py             # Badge models
│   └── schemas/
│       ├── __init__.py
│       ├── user.py              # User schemas
│       ├── challenge.py         # Challenge schemas
│       ├── progress.py          # Progress schemas
│       └── badge.py             # Badge schemas
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
└── README.md                    # This file
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   cd sleePY
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   On Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update the values (especially `SECRET_KEY` for production)

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

   Or:
   ```bash
   python main.py
   ```

7. **Access the application**
   - API: http://localhost:8000
   - Interactive API docs (Swagger UI): http://localhost:8000/docs
   - Alternative API docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Create a new user account
- `POST /api/auth/login` - Login with username and password

### Users

- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile
- `GET /api/users/me/stats` - Get current user statistics
- `GET /api/users/leaderboard` - Get top users leaderboard
- `GET /api/users/{user_id}` - Get user profile by ID

### Challenges

- `GET /api/challenges/` - Get list of challenges (paginated, filterable)
- `GET /api/challenges/{challenge_id}` - Get specific challenge
- `POST /api/challenges/` - Create new challenge (admin only)
- `PUT /api/challenges/{challenge_id}` - Update challenge (admin only)
- `DELETE /api/challenges/{challenge_id}` - Delete challenge (admin only)

### Progress

- `GET /api/progress/` - Get all progress records for current user
- `GET /api/progress/{challenge_id}` - Get progress for specific challenge
- `POST /api/progress/start/{challenge_id}` - Start a challenge
- `POST /api/progress/submit` - Submit code for a challenge
- `GET /api/progress/completed` - Get all completed challenges

### Badges

- `GET /api/badges/` - Get all available badges
- `GET /api/badges/my-badges` - Get current user's earned badges
- `GET /api/badges/{badge_id}` - Get specific badge
- `POST /api/badges/` - Create new badge (admin only)
- `POST /api/badges/award/{user_id}/{badge_id}` - Award badge to user (admin only)
- `DELETE /api/badges/{badge_id}` - Delete badge (admin only)

## Usage Examples

### 1. Sign Up
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "pythonmaster",
    "email": "master@python.com",
    "password": "securepass123",
    "full_name": "Python Master"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=pythonmaster&password=securepass123"
```

### 3. Get Challenges (with auth token)
```bash
curl -X GET "http://localhost:8000/api/challenges/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Submit Challenge Code
```bash
curl -X POST "http://localhost:8000/api/progress/submit" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": 1,
    "code": "def hello():\n    return \"Hello World\""
  }'
```

## Database

### SQLite (Default - Local Development)

The application uses SQLite by default. The database file `pyquest.db` will be created automatically in the project root when you first run the application.

### PostgreSQL (Production)

To use PostgreSQL:

1. Install PostgreSQL
2. Create a database:
   ```sql
   CREATE DATABASE pyquest_db;
   ```
3. Update `.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/pyquest_db
   ```
4. Restart the application

## Gamification System

### Experience Points (XP)

- Users earn XP by completing challenges
- XP amount varies by challenge difficulty:
  - Beginner: 10 XP
  - Intermediate: 15 XP
  - Advanced: 20 XP
  - Expert: 30 XP

### Levels

Users level up automatically based on XP:
- Level 1: 0-99 XP
- Level 2: 100-399 XP
- Level 3: 400-899 XP
- Level 4: 900-1599 XP
- And so on...

Formula: `level = floor(sqrt(xp / 100)) + 1`

### Badges

Badges are achievements that can be awarded to users for:
- Completing their first challenge
- Reaching certain levels
- Completing all challenges in a category
- Maintaining learning streaks
- And more (customizable by admins)

## Development

### Creating an Admin User

Currently, users are created as regular users by default. To create an admin user, you'll need to manually update the database:

```python
# In a Python shell with your app context
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "yourusername").first()
user.is_superuser = True
db.commit()
```

### Adding Sample Challenges

Use the API or create a script to populate challenges:

```python
# sample_data.py
from app.db.session import SessionLocal
from app.models.challenge import Challenge, DifficultyLevel, ChallengeCategory

db = SessionLocal()

challenge = Challenge(
    title="Hello World",
    description="Create your first Python function",
    instructions="Write a function that returns 'Hello World'",
    difficulty=DifficultyLevel.BEGINNER,
    category=ChallengeCategory.BASICS,
    starter_code="def hello_world():\n    # Your code here\n    pass",
    solution="def hello_world():\n    return 'Hello World'",
    xp_reward=10,
    required_level=1,
    order=1
)

db.add(challenge)
db.commit()
```

## Testing

The project includes pytest configuration. To run tests:

```bash
pytest
```

## Security Notes

- Change `SECRET_KEY` in production (generate with `openssl rand -hex 32`)
- Use HTTPS in production
- Set `DEBUG=False` in production
- Use environment variables for sensitive data
- Regularly update dependencies

## Future Enhancements

- [ ] Code execution sandbox for running user submissions
- [ ] Real test case validation
- [ ] Learning paths and course structures
- [ ] Social features (friends, challenges)
- [ ] Daily/weekly challenges
- [ ] Achievement system expansion
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Rate limiting
- [ ] Caching layer

## License

MIT License - feel free to use this project for learning or commercial purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Built with FastAPI and Python
