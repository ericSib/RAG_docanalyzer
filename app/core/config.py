from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class AnalyzerConfig:
    """Configuration settings for the document analyzer."""
    CHUNK_SIZE: int = 512
    OVERLAP_SIZE: int = 50
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    SPACY_MODEL: str = "fr_core_news_lg"
    
    # Quality thresholds
    MIN_CHUNK_LENGTH: int = 100
    TEXT_QUALITY_THRESHOLD: float = 0.8
    EMBEDDING_QUALITY_THRESHOLD: float = 0.85
    
    # Processing settings
    BATCH_SIZE: int = 10
    MAX_PARALLEL_PROCESSES: int = 4
    
    # File type settings
    SUPPORTED_EXTENSIONS: list = [".pdf", ".docx", ".pptx", ".txt"]
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_')
        }

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "RAG Document Analyzer"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rag_analyzer")
    
    # Storage Settings
    UPLOAD_DIR: str = "data/uploads"
    CACHE_DIR: str = "data/cache"
    EXPORT_DIR: str = "data/exports"
    
    # Cache Settings
    CACHE_TTL: int = 24 * 60 * 60  # 24 hours in seconds
    MAX_CACHE_SIZE: int = 1024 * 1024 * 1024  # 1GB
    
    # Analyzer Settings
    ANALYZER: AnalyzerConfig = AnalyzerConfig
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Export configuration for easy access
analyzer_config = settings.ANALYZER.as_dict()
