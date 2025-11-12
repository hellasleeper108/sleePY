# PyQuest Deployment Guide

Complete guide for deploying PyQuest - A Gamified Python Learning Platform

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
  - [Render](#deploy-to-render)
  - [Vercel](#deploy-frontend-to-vercel)
- [CI/CD Setup](#cicd-setup)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Overview

PyQuest is a full-stack application with:
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 14 (React, TypeScript)
- **Database**: PostgreSQL 15
- **Caching**: In-memory (Redis-ready)
- **AI Integration**: Ollama, OpenAI, Claude

---

## Architecture

```
┌──────────────┐
│   Frontend   │  Next.js (Port 3000)
│  (Next.js)   │
└──────┬───────┘
       │
┌──────▼───────┐
│    Nginx     │  Reverse Proxy (Port 80/443)
│  (Optional)  │
└──────┬───────┘
       │
┌──────▼───────┐
│   Backend    │  FastAPI (Port 8000)
│  (FastAPI)   │
└──────┬───────┘
       │
┌──────▼───────┐
│  PostgreSQL  │  Database (Port 5432)
└──────────────┘
```

---

## Prerequisites

### Required
- **Docker** 20.10+ and Docker Compose 2.0+
- **Git**
- **Python** 3.11+ (for local development)
- **Node.js** 20+ (for local development)

### Optional (for AI features)
- **OpenAI API Key** - GPT-3.5/GPT-4
- **Anthropic API Key** - Claude
- **Ollama** - Local LLM server

---

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sleePY.git
cd sleePY
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (auto-runs on startup)
python main.py
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Docker Deployment

### Quick Start

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Services

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Database**: localhost:5432
- **Nginx** (optional): http://localhost:80

### Production with Nginx

```bash
# Start with production profile
docker-compose --profile production up -d

# This includes nginx reverse proxy
# Access everything through: http://localhost
```

### Database Migrations

```bash
# Database tables are created automatically on first run

# To reset database
docker-compose down -v
docker-compose up -d
```

### Useful Docker Commands

```bash
# View running containers
docker-compose ps

# Restart a service
docker-compose restart backend

# View backend logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python -c "print('Hello')"

# Rebuild after code changes
docker-compose up -d --build
```

---

## Cloud Deployment

### Deploy to Render

Render provides free hosting for PostgreSQL, web services, and static sites.

#### 1. Create Render Account
- Sign up at https://render.com
- Connect your GitHub repository

#### 2. Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `pyquest-db`
3. Database: `pyquest`
4. User: `pyquest`
5. Region: Choose closest to you
6. Plan: Free (or paid for production)
7. Click "Create Database"
8. Copy the "Internal Database URL" for use in backend

#### 3. Deploy Backend
1. Click "New +" → "Web Service"
2. Connect repository
3. Configure:
   - **Name**: `pyquest-backend`
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: Free or Starter
4. Add Environment Variables:
   ```
   DATABASE_URL=<internal-database-url-from-step-2>
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
   OPENAI_API_KEY=sk-... (optional)
   ANTHROPIC_API_KEY=sk-ant-... (optional)
   ```
5. Click "Create Web Service"
6. Copy the backend URL (e.g., `https://pyquest-backend.onrender.com`)

#### 4. Enable GitHub Actions Deploy Hook (Optional)
1. Go to backend service → Settings
2. Scroll to "Deploy Hook"
3. Copy the deploy hook URL
4. Add to GitHub Secrets as `RENDER_DEPLOY_HOOK`

### Deploy Frontend to Vercel

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Deploy Frontend
```bash
cd frontend

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://pyquest-backend.onrender.com
```

#### 3. Configure Custom Domain (Optional)
1. Go to Vercel dashboard
2. Select your project
3. Settings → Domains
4. Add your custom domain

---

## CI/CD Setup

### GitHub Actions

The repository includes a CI/CD pipeline that:
- ✅ Runs backend tests with PostgreSQL
- ✅ Runs frontend linting and builds
- ✅ Builds and pushes Docker images to GitHub Container Registry
- ✅ Deploys to Render (if configured)
- ✅ Deploys to Vercel (if configured)

### Required GitHub Secrets

Add these in: Settings → Secrets and variables → Actions

#### For Docker Registry
- `GITHUB_TOKEN` - Automatically provided

#### For Render Deployment
- `RENDER_DEPLOY_HOOK` - From Render service settings

#### For Vercel Deployment
- `VERCEL_TOKEN` - From Vercel account settings
- `VERCEL_ORG_ID` - From Vercel project settings
- `VERCEL_PROJECT_ID` - From Vercel project settings
- `NEXT_PUBLIC_API_URL` - Your backend URL

### Trigger Deployment

```bash
# Commit and push to main/master branch
git add .
git commit -m "Deploy to production"
git push origin main

# Or manually trigger in GitHub Actions tab
```

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/database
POSTGRES_USER=pyquest
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=pyquest

# Security (IMPORTANT: Change in production!)
SECRET_KEY=generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://your-domain.com"]

# AI Providers (Optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434

# App Config
APP_NAME=PyQuest
APP_VERSION=1.0.0
```

### Frontend

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
# Or in production: https://your-backend.onrender.com
```

### Generate Secure SECRET_KEY

```bash
openssl rand -hex 32
```

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database connection failed
#    → Check DATABASE_URL in .env
#    → Ensure postgres container is running

# 2. Port already in use
#    → Change BACKEND_PORT in .env
#    → Or stop conflicting service

# 3. Missing dependencies
#    → Rebuild: docker-compose up -d --build
```

### Frontend won't build

```bash
# Check logs
docker-compose logs frontend

# Common issues:
# 1. Node modules not installed
#    → docker-compose exec frontend npm install

# 2. API URL not set
#    → Check NEXT_PUBLIC_API_URL in .env

# 3. Build cache issues
#    → docker-compose build --no-cache frontend
```

### Database connection issues

```bash
# Check if database is running
docker-compose ps

# Test connection
docker-compose exec db psql -U pyquest -d pyquest

# Reset database
docker-compose down -v
docker-compose up -d
```

### AI Mentor not working

```bash
# Check if AI provider is configured
docker-compose exec backend python -c "from app.services.ai_providers import LLMProviderFactory; print(LLMProviderFactory.get_available_provider())"

# For Ollama
# 1. Install Ollama on host
# 2. Pull a model: ollama pull mistral
# 3. Update OLLAMA_BASE_URL to http://host.docker.internal:11434

# For OpenAI/Claude
# 1. Add API keys to .env
# 2. Restart backend
```

### Performance issues

```bash
# Check resource usage
docker stats

# Increase Docker resources in Docker Desktop settings
# Recommended: 4 GB RAM, 2 CPU cores

# Enable caching in production
# Add Redis container to docker-compose.yml
```

---

## Monitoring

### Health Checks

- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000
- Database: `docker-compose exec db pg_isready`

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Analytics Dashboard

- Access admin dashboard at: http://localhost:3000/admin
- Requires admin user (set `is_superuser = True` in database)

---

## Security Checklist

- [ ] Change default `SECRET_KEY` in production
- [ ] Use strong database passwords
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable rate limiting in nginx
- [ ] Keep dependencies updated
- [ ] Restrict admin access
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/sleePY/issues
- Documentation: https://github.com/yourusername/sleePY
- Email: support@pyquest.com

---

## License

This project is licensed under the MIT License.
