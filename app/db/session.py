"""
Database session management and configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings


# Create database engine
# SQLite for local dev, easily switchable to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True,  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session

    Usage in FastAPI endpoints:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()

    Yields:
        Session: Database session

    The session is automatically closed after the request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables

    Call this on application startup
    """
    from app.db.base import Base
    from app.models import User, Challenge, Progress, Badge, UserBadge

    # Import all models to ensure they're registered with Base
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
