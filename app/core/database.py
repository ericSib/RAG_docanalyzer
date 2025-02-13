"""
Database configuration module for PostgreSQL with pgvector support.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.engine import Engine
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "rag_doc_analyzer")

# Connection URLs
SYNC_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create engines
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

# Create session factories
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@event.listens_for(Engine, "connect")
def connect(dbapi_connection, connection_record):
    """Enable pgvector extension on database connection."""
    with dbapi_connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

def init_db() -> None:
    """Initialize database with required extensions and tables."""
    from app.models.document import Base
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def get_db() -> Session:
    """Synchronous database session generator."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Asynchronous database session generator."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def check_db_connection() -> bool:
    """Check if database connection is working."""
    try:
        with sync_engine.connect() as conn:
            conn.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

# Example usage of session with context manager
class DatabaseSessionManager:
    """Context manager for database sessions."""
    
    def __init__(self, session_factory=SyncSessionLocal):
        self.session_factory = session_factory
    
    def __enter__(self) -> Session:
        self.session = self.session_factory()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        self.session.close()
