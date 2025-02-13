from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chemin de la base de données SQLite
DB_PATH = Path("rag_docs.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

# Création de la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_db_connection() -> bool:
    """Vérifie la connexion à la base de données."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info(f"Test connexion DB réussi: {value}")
            return value == 1
    except Exception as e:
        logger.error(f"Erreur connexion DB: {str(e)}")
        return False

def get_db():
    """Crée une nouvelle session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> bool:
    """Initialise la base de données."""
    from .models import Base  # Import ici pour éviter les imports circulaires
    
    try:
        # Création des tables
        Base.metadata.create_all(bind=engine)
        logger.info(f"Base de données initialisée: {DB_PATH}")
        
        # Vérification de la connexion
        if not check_db_connection():
            raise Exception("Échec de la vérification de connexion")
            
        return True
    except Exception as e:
        logger.error(f"Erreur initialisation DB: {str(e)}")
        return False
