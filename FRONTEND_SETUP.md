# PyQuest - Complete Setup Guide

This guide will help you run both the backend (FastAPI) and frontend (Next.js) for PyQuest.

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Backend Setup (FastAPI)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize the Database

```bash
python init_sample_data.py
```

This will create:
- SQLite database with tables
- Sample admin user (username: `admin`, password: `admin123`)
- 8 sample coding challenges
- 7 badges
- 17 achievements
- 5 learning paths with 12 lessons

### 3. Run the Backend Server

```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using python
python main.py
```

The backend will be available at: http://localhost:8000

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Frontend Setup (Next.js)

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

### 3. Configure Environment

Create a `.env.local` file:

```bash
cp .env.example .env.local
```

The default configuration should work:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run the Development Server

```bash
npm run dev
```

The frontend will be available at: http://localhost:3000

## Running Both Services

For the best experience, run both services simultaneously:

### Terminal 1 - Backend
```bash
python main.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Test Account

Use the pre-created admin account to log in:
- **Username:** `admin`
- **Password:** `admin123`

Or create a new account through the registration endpoint.

## Features to Explore

### Dashboard (http://localhost:3000)
- View your stats, XP, level, and streak
- Track achievements and loot chests
- See overall progress

### Quest Board (http://localhost:3000/quests)
- Browse all coding challenges
- Filter by difficulty and completion status
- See XP rewards and challenge details

### Learning Paths (http://localhost:3000/paths)
- Explore structured Python courses
- Complete interactive lessons
- Earn XP and badges

### Code Arena
- Access through the backend at: http://localhost:8000/api/arena/arena
- Write and run Python code in the browser
- Real-time test execution with Pyodide
- Automatic XP rewards on success

### Achievements (http://localhost:3000/achievements)
- View all available achievements
- Track your progress
- See unlocked achievements

### Profile (http://localhost:3000/profile)
- View account information
- Check your stats
- See your progress

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register new user
- `GET /api/users/me` - Get current user

### Challenges
- `GET /api/challenges` - List all challenges
- `GET /api/challenges/{id}` - Get challenge details

### Progress
- `GET /api/progress/me` - Get your progress
- `POST /api/progress/submit` - Submit code solution

### Game Mechanics
- `GET /api/game/stats` - Get user stats
- `GET /api/game/streak` - Get daily streak
- `POST /api/game/checkin` - Daily check-in
- `GET /api/game/chests` - List loot chests
- `POST /api/game/chests/{id}/open` - Open chest
- `GET /api/game/achievements` - List achievements

### Learning Paths
- `GET /api/paths` - List learning paths
- `GET /api/paths/{id}` - Get path details
- `GET /api/paths/{id}/lessons` - Get lessons
- `POST /api/paths/{id}/lessons/{lesson_id}/complete` - Complete lesson

## Technology Stack

### Backend
- **Framework:** FastAPI
- **Database:** SQLAlchemy with SQLite
- **Authentication:** JWT with bcrypt
- **Validation:** Pydantic

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Markdown:** react-markdown
- **Icons:** Lucide React

## Troubleshooting

### Backend Issues

**ModuleNotFoundError:**
```bash
pip install -r requirements.txt
```

**Database errors:**
```bash
# Delete and recreate the database
rm pyquest.db
python init_sample_data.py
```

**Port already in use:**
```bash
# Change the port in main.py or use:
uvicorn main:app --reload --port 8001
```

### Frontend Issues

**Cannot find module:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Ensure backend is running on port 8000
- Check `.env.local` has correct API URL
- Verify CORS settings in backend

**Build errors:**
```bash
cd frontend
npm run build
```

## Development Tips

### Backend
- Use `/docs` for interactive API documentation
- Check logs for debugging
- Use SQLite Browser to inspect database

### Frontend
- Use React DevTools for component debugging
- Check browser console for errors
- Use Network tab to inspect API calls

## Production Build

### Backend
```bash
# Use production ASGI server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

## Next Steps

1. Complete some challenges to earn XP
2. Explore learning paths
3. Unlock achievements
4. Open loot chests
5. Maintain your daily streak

Enjoy your gamified Python learning journey with PyQuest! 🚀
