"""
Database configuration for VoiceTree
GitHub Issue #1: FastAPI backend setup with SQLite database
Supports PostgreSQL for production via DATABASE_URL environment variable
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable or use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production: Use PostgreSQL
    # Handle Railway/Render postgres:// URL format (needs to be postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    # Create engine without SQLite-specific arguments
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # Development: Use SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./voicetree.db"
    # Create SQLAlchemy engine with SQLite-specific settings
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)
