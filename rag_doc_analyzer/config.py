import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "rag_docs.db"

# Création des dossiers nécessaires
DATA_DIR.mkdir(exist_ok=True)

# Configuration de la base de données
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Configuration spaCy
SPACY_MODEL = "fr_core_news_md"
SENTENCE_TRANSFORMER_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Configuration du logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "app.log"
