"""
Configuration centrale de l'application.
Charge les variables d'environnement et fournit les paramètres de configuration.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis .env
load_dotenv()

class Settings(BaseSettings):
    """Configuration de l'application basée sur les variables d'environnement."""
    
    # Configuration de base
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Configuration de l'API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Limites et seuils
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_TOKENS_PER_REQUEST: int = 1_000_000
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Modèles et paramètres
    SPACY_MODEL: str = "fr_core_news_md"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    
    # Logs et monitoring
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    # Chemins
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    LOGS_DIR: Path = BASE_DIR / "logs"
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    
    class Config:
        """Configuration Pydantic."""
        env_file = ".env"
        case_sensitive = True

    def setup_directories(self) -> None:
        """Crée les répertoires nécessaires s'ils n'existent pas."""
        for directory in [self.LOGS_DIR, self.DATA_DIR, self.MODELS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Instance unique des paramètres
settings = Settings()

# Création des répertoires nécessaires
settings.setup_directories()