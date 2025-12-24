"""
Database connection and session management.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings

settings = get_settings()

# Create database URL - handle Render's postgres:// vs postgresql://
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes that need database access.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI routes.
    Use with 'with get_db_session() as db:' syntax.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all database tables based on the models.
    Called at application startup.
    """
    # Import Base and all models to register them
    from app.models.base import Base
    from app.models import User, Level, Attempt, LevelCompletion, Session, AuditLog
    
    Base.metadata.create_all(bind=engine)
