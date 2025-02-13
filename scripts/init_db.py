"""
Initialize the database and pgvector extension.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv(encoding='utf-8')

def create_database():
    """Create the database if it doesn't exist."""
    # Connect to default database to create new database
    default_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/postgres"
    engine = create_engine(default_url, echo=True)
    
    # Create database if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Close any open transaction
        try:
            conn.execute(text(f"CREATE DATABASE {os.getenv('DB_NAME', 'rag_doc_analyzer')}"))
            logger.info(f"Database {os.getenv('DB_NAME', 'rag_doc_analyzer')} created successfully")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Database {os.getenv('DB_NAME', 'rag_doc_analyzer')} already exists")
            else:
                logger.error(f"Error creating database: {str(e)}")
                raise

def setup_pgvector():
    """Setup pgvector extension."""
    # Connect to the target database
    database_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'rag_doc_analyzer')}"
    engine = create_engine(database_url, echo=True)
    
    # Create pgvector extension
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(text("COMMIT"))
            logger.info("pgvector extension enabled successfully")
        except Exception as e:
            logger.error(f"Error enabling pgvector extension: {str(e)}")
            raise

def main():
    """Main function to initialize database and extensions."""
    try:
        create_database()
        setup_pgvector()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
