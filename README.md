# 🐍 PyQuest - Gamified Python Learning Platform

A comprehensive, gamified learning platform where users complete coding challenges, earn XP, level up, unlock achievements, and compete with friends while mastering Python programming.

[![CI/CD](https://github.com/yourusername/sleePY/actions/workflows/deploy.yml/badge.svg)](https://github.com/yourusername/sleePY/actions/workflows/deploy.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

### 🎮 Core Gamification
- **XP & Leveling System** - Earn experience points and level up
- **Dynamic Level Calculation** - Progressive XP requirements
- **Loot Chests** - Random rewards (Common → Legendary)
- **Daily Streaks** - Consecutive login rewards
- **Achievements** - 50+ unlockable achievements
- **Badges** - Collectible badges for milestones

### 💻 Learning Features
- **Coding Challenges** - 100+ Python challenges across difficulty levels
- **Learning Paths** - Structured courses (Basics, Data Structures, OOP, Algorithms, Web Dev)
- **Browser-Based Code Arena** - Pyodide-powered Python execution
- **Mentor AI** - Progressive hint system with bonus XP rewards
  - Ollama, OpenAI, and Claude support
  - Context-aware hints based on user code and errors
  - Bonus XP for solving with fewer hints (0 hints: +20%, 1 hint: +10%, 2 hints: +5%)

### 🏆 Community & Competition
- **Leaderboards** - Global, weekly, and topic-based rankings
- **Friend System** - Follow users and track their progress
- **Challenge Duels** - 1v1 coding competitions with XP stakes
- **Real-time Rankings** - Auto-updating leaderboards with 5-minute cache

### 📊 Analytics & Insights (Admin)
- **Performance Tracking** - Time spent per challenge
- **Completion Rates** - Topic-wise success rates
- **User Engagement** - DAU, WAU, MAU metrics
- **XP Distribution** - User progression analysis
- **Interactive Charts** - Chart.js visualizations

### 🔐 User Management
- **JWT Authentication** - Secure token-based auth
- **Role-Based Access** - User and admin roles
- **Profile Management** - User stats and achievements
- **Session Tracking** - Challenge attempt timing

## 🚀 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL ORM with PostgreSQL
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Uvicorn** - ASGI server
- **httpx** - Async HTTP client for AI providers

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Data visualization
- **Pyodide** - Browser-based Python execution

### Infrastructure
- **Docker** - Containerization
- **PostgreSQL 15** - Production database
- **Nginx** - Reverse proxy
- **GitHub Actions** - CI/CD pipeline

### AI Integration
- **Ollama** - Local LLM support
- **OpenAI GPT** - GPT-3.5/GPT-4
- **Anthropic Claude** - Claude API

## 📦 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/sleePY.git
cd sleePY

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Dashboard: http://localhost:3000/admin

### Local Development

#### Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 🌐 Deployment

### Deploy to Render (Backend + Database)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click "Deploy to Render" button above
2. Connect your GitHub repository
3. Configure environment variables
4. Deploy!

Detailed instructions: See [DEPLOYMENT.md](DEPLOYMENT.md)

### Deploy to Vercel (Frontend)

```bash
cd frontend
npm install -g vercel
vercel --prod
```

Set `NEXT_PUBLIC_API_URL` to your Render backend URL.

### Full Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:
- Docker deployment
- Cloud deployment (Render, Vercel)
- CI/CD setup with GitHub Actions
- Environment configuration
- Monitoring and troubleshooting

## 📚 Documentation

### API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Project Structure

```
sleePY/
├── app/
│   ├── api/endpoints/       # API route handlers
│   │   ├── auth.py          # Authentication
│   │   ├── users.py         # User management
│   │   ├── challenges.py    # Coding challenges
│   │   ├── progress.py      # Progress tracking
│   │   ├── game.py          # Gamification (XP, streaks, chests)
│   │   ├── badges.py        # Badge system
│   │   ├── learning_paths.py # Learning courses
│   │   ├── code_arena.py    # Code execution
│   │   ├── friends.py       # Social features
│   │   ├── duels.py         # Challenge competitions
│   │   ├── leaderboard.py   # Rankings
│   │   ├── mentor.py        # AI mentor hints
│   │   └── analytics.py     # Performance metrics
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── game_engine.py   # Gamification engine
│   │   ├── code_execution.py # Code runner
│   │   ├── leaderboard.py   # Leaderboard service
│   │   ├── mentor.py        # AI mentor service
│   │   ├── ai_providers.py  # AI provider abstraction
│   │   └── analytics.py     # Analytics service
│   ├── core/                # Core utilities
│   └── db/                  # Database configuration
├── frontend/
│   ├── app/                 # Next.js pages
│   │   ├── page.tsx         # Dashboard
│   │   ├── quests/          # Challenge board
│   │   ├── arena/[id]/      # Code arena
│   │   ├── paths/           # Learning paths
│   │   ├── achievements/    # Achievements page
│   │   ├── leaderboard/     # Rankings
│   │   ├── social/          # Friends & duels
│   │   ├── profile/         # User profile
│   │   └── admin/           # Analytics dashboard
│   ├── components/          # React components
│   └── lib/                 # Utilities & API client
├── nginx/                   # Nginx configuration
├── .github/workflows/       # CI/CD pipelines
├── Dockerfile               # Backend container
├── docker-compose.yml       # Multi-container setup
├── render.yaml              # Render deployment config
└── DEPLOYMENT.md            # Deployment guide
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/pyquest

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# AI Providers (Optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

### Generate Secure Secret Key

```bash
openssl rand -hex 32
```

## 🎯 Key Features Breakdown

### Mentor AI System
- Progressive 3-level hint system
- Context-aware based on user code and errors
- Bonus XP rewards for self-sufficiency
- Support for multiple AI providers (Ollama, OpenAI, Claude)
- Fallback to mock provider for offline development

### Leaderboard System
- In-memory caching with 5-minute TTL
- Auto-invalidation on XP changes
- Optimized PostgreSQL queries with indexes
- Global, weekly, and topic-based rankings
- Friend leaderboards for social comparison

### Analytics Dashboard
- Real-time engagement metrics (DAU, WAU, MAU)
- Challenge time tracking with avg/min/max
- Topic completion rates
- XP distribution across user base
- Interactive Chart.js visualizations
- Admin-only access with role verification

### Duel System
- 1v1 challenge competitions
- Configurable XP stakes (10-500 XP)
- Winner determination based on completion time
- Bonus XP for both participants
- 24-hour acceptance window
- Expiration and cancellation handling

## 🧪 Testing

```bash
# Backend tests
pytest --cov=app

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 📈 CI/CD

GitHub Actions pipeline automatically:
- ✅ Runs tests on push/PR
- ✅ Builds Docker images
- ✅ Pushes to GitHub Container Registry
- ✅ Deploys to Render (backend)
- ✅ Deploys to Vercel (frontend)

See `.github/workflows/deploy.yml` for configuration.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - For the amazing web framework
- **Next.js** - For the powerful React framework
- **Pyodide** - For browser-based Python execution
- **Chart.js** - For beautiful data visualizations
- **Ollama** - For local LLM support

## 📧 Support

- 📫 Email: support@pyquest.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/sleePY/issues)
- 📖 Docs: [Deployment Guide](DEPLOYMENT.md)

## 🗺️ Roadmap

- [ ] Real-time multiplayer duels with WebSockets
- [ ] Team challenges and tournaments
- [ ] Video tutorials and explanations
- [ ] Mobile app (React Native)
- [ ] Code review system with AI feedback
- [ ] Certification system
- [ ] Integration with GitHub for portfolio
- [ ] Discord bot for notifications

---

**Built with ❤️ by the PyQuest Team**

⭐ Star us on GitHub if you find this project useful!
