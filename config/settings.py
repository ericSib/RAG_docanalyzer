"""Configuration de l'application."""
import os
from pathlib import Path
from typing import Optional, List
import json
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class MLConfig:
    """Configuration des modèles ML."""
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    spacy_model: str = "fr_core_news_md"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    models_dir: str = "resources/ml_models"
    cache_dir: str = "data/cache/models"

@dataclass
class StorageConfig:
    """Configuration du stockage."""
    db_path: str = "data/rag.db"
    documents_dir: str = "data/documents"
    models_dir: str = "data/models"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: List[str] = field(default_factory=lambda: ["txt", "pdf", "doc", "docx"])

@dataclass
class LoggingConfig:
    """Configuration du logging."""
    level: str = "INFO"
    file: str = "logs/rag.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class AIConfig:
    """Configuration de l'IA."""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=lambda: ["\n\n", "###"])

@dataclass
class AppConfig:
    """Configuration de l'application."""
    name: str = "RAG Analyzer"
    version: str = "1.0.0"
    description: str = "Application d'analyse de documents avec RAG"
    author: str = "Codeium"
    license: str = "MIT"

@dataclass
class Config:
    """Configuration principale."""
    ml: MLConfig = field(default_factory=MLConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    app: AppConfig = field(default_factory=AppConfig)
    debug: bool = False
    env: str = "development"
    
    @classmethod
    def load(
        cls,
        default_config: Optional[Path] = None,
        env_config: Optional[Path] = None
    ) -> 'Config':
        """Charge la configuration.
        
        Args:
            default_config: Chemin du fichier de configuration par défaut
            env_config: Chemin du fichier de configuration d'environnement
            
        Returns:
            Configuration chargée
        """
        # Configuration par défaut
        config = cls()
        
        def load_config_file(path: Path) -> Dict[str, Any]:
            """Charge un fichier de configuration."""
            if path and path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
            return {}
        
        # Charge la configuration par défaut
        default_data = load_config_file(default_config)
        
        # Charge la configuration d'environnement
        env_data = load_config_file(env_config)
        
        # Fusionne les configurations
        data = {**default_data, **env_data}
        
        # ML
        if 'ml' in data:
            config.ml = MLConfig(
                embedding_model=data['ml'].get('embedding_model', config.ml.embedding_model),
                spacy_model=data['ml'].get('spacy_model', config.ml.spacy_model),
                chunk_size=data['ml'].get('chunk_size', config.ml.chunk_size),
                chunk_overlap=data['ml'].get('chunk_overlap', config.ml.chunk_overlap),
                models_dir=data['ml'].get('models_dir', config.ml.models_dir),
                cache_dir=data['ml'].get('cache_dir', config.ml.cache_dir)
            )
        
        # Storage
        if 'storage' in data:
            config.storage = StorageConfig(
                db_path=data['storage'].get('db_path', config.storage.db_path),
                documents_dir=data['storage'].get('documents_dir', config.storage.documents_dir),
                models_dir=data['storage'].get('models_dir', config.storage.models_dir),
                max_file_size=data['storage'].get('max_file_size', config.storage.max_file_size),
                supported_formats=data['storage'].get('supported_formats', config.storage.supported_formats)
            )
        
        # Logging
        if 'logging' in data:
            config.logging = LoggingConfig(
                level=data['logging'].get('level', config.logging.level),
                file=data['logging'].get('file', config.logging.file),
                format=data['logging'].get('format', config.logging.format),
                max_size=data['logging'].get('max_size', config.logging.max_size),
                backup_count=data['logging'].get('backup_count', config.logging.backup_count)
            )
        
        # AI
        if 'ai' in data:
            config.ai = AIConfig(
                temperature=data['ai'].get('temperature', config.ai.temperature),
                max_tokens=data['ai'].get('max_tokens', config.ai.max_tokens),
                top_p=data['ai'].get('top_p', config.ai.top_p),
                frequency_penalty=data['ai'].get('frequency_penalty', config.ai.frequency_penalty),
                presence_penalty=data['ai'].get('presence_penalty', config.ai.presence_penalty),
                stop_sequences=data['ai'].get('stop_sequences', config.ai.stop_sequences)
            )
        
        # App
        if 'app' in data:
            config.app = AppConfig(
                name=data['app'].get('name', config.app.name),
                version=data['app'].get('version', config.app.version),
                description=data['app'].get('description', config.app.description),
                author=data['app'].get('author', config.app.author),
                license=data['app'].get('license', config.app.license)
            )
        
        # Autres paramètres
        config.debug = data.get('debug', config.debug)
        config.env = data.get('env', config.env)
        
        # Surcharge avec les variables d'environnement
        config.ml.embedding_model = os.getenv('RAG_EMBEDDING_MODEL', config.ml.embedding_model)
        config.ml.spacy_model = os.getenv('RAG_SPACY_MODEL', config.ml.spacy_model)
        config.ml.chunk_size = int(os.getenv('RAG_CHUNK_SIZE', str(config.ml.chunk_size)))
        config.ml.chunk_overlap = int(os.getenv('RAG_CHUNK_OVERLAP', str(config.ml.chunk_overlap)))
        config.ml.models_dir = os.getenv('RAG_MODELS_DIR', config.ml.models_dir)
        config.ml.cache_dir = os.getenv('RAG_CACHE_DIR', config.ml.cache_dir)
        
        config.storage.db_path = os.getenv('RAG_DB_PATH', config.storage.db_path)
        config.storage.documents_dir = os.getenv('RAG_DOCUMENTS_DIR', config.storage.documents_dir)
        config.storage.models_dir = os.getenv('RAG_MODELS_DIR', config.storage.models_dir)
        config.storage.max_file_size = int(os.getenv('RAG_MAX_FILE_SIZE', str(config.storage.max_file_size)))
        
        config.logging.level = os.getenv('RAG_LOG_LEVEL', config.logging.level)
        config.logging.file = os.getenv('RAG_LOG_FILE', config.logging.file)
        config.logging.max_size = int(os.getenv('RAG_LOG_MAX_SIZE', str(config.logging.max_size)))
        config.logging.backup_count = int(os.getenv('RAG_LOG_BACKUP_COUNT', str(config.logging.backup_count)))
        
        config.ai.temperature = float(os.getenv('RAG_AI_TEMPERATURE', str(config.ai.temperature)))
        config.ai.max_tokens = int(os.getenv('RAG_AI_MAX_TOKENS', str(config.ai.max_tokens)))
        config.ai.top_p = float(os.getenv('RAG_AI_TOP_P', str(config.ai.top_p)))
        
        config.debug = os.getenv('RAG_DEBUG', str(config.debug)).lower() == 'true'
        config.env = os.getenv('RAG_ENV', config.env)
        
        return config

# Instance unique des paramètres
config = Config.load()
