"""
PyQuest - Gamified Python Learning Platform
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import init_db
from app.api.endpoints import auth, users, challenges, progress, badges, game, learning_paths, code_arena


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events

    Runs on startup and shutdown
    """
    # Startup
    print("Starting PyQuest backend...")
    print(f"Database URL: {settings.DATABASE_URL}")

    # Initialize database tables
    init_db()

    yield

    # Shutdown
    print("Shutting down PyQuest backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A gamified Python learning platform with RPG mechanics: coding challenges, XP, levels, loot chests, daily streaks, and achievements",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def root():
    """
    Root endpoint - API health check

    Returns:
        dict: API status and info
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "message": "Welcome to PyQuest! Visit /docs for API documentation."
    }


# Include routers
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"]
)

app.include_router(
    challenges.router,
    prefix="/api/challenges",
    tags=["Challenges"]
)

app.include_router(
    progress.router,
    prefix="/api/progress",
    tags=["Progress"]
)

app.include_router(
    badges.router,
    prefix="/api/badges",
    tags=["Badges"]
)

app.include_router(
    game.router,
    prefix="/api/game",
    tags=["Game Mechanics"]
)

app.include_router(
    learning_paths.router,
    prefix="/api/paths",
    tags=["Learning Paths"]
)

app.include_router(
    code_arena.router,
    prefix="/api/arena",
    tags=["Code Arena"]
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    # Run with: python main.py
    # Or better: uvicorn main:app --reload
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )
