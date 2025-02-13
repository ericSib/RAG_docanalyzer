"""Configuration de l'application."""
from pathlib import Path
from .settings import Config

# Répertoire de configuration
CONFIG_DIR = Path(__file__).parent

# Charge la configuration par défaut
config = Config.load(
    default_config=CONFIG_DIR / 'defaults/default.json',
    env_config=CONFIG_DIR / 'defaults/development.json'
)
