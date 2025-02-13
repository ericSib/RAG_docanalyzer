"""Configuration des tests pour pytest."""
import os
import pytest
from pathlib import Path
from typing import Generator

# Racine du projet
@pytest.fixture(scope="session")
def project_root() -> Path:
    """Retourne le chemin racine du projet."""
    return Path(__file__).parent.parent

# Fixtures pour les chemins de données de test
@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Retourne le chemin du répertoire de données de test."""
    path = project_root / "tests" / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path

@pytest.fixture(scope="session")
def test_documents_dir(test_data_dir: Path) -> Path:
    """Retourne le chemin du répertoire de documents de test."""
    path = test_data_dir / "documents"
    path.mkdir(parents=True, exist_ok=True)
    return path

# Fixtures pour la base de données de test
@pytest.fixture(scope="function")
def test_db_path(test_data_dir: Path) -> Generator[Path, None, None]:
    """Retourne le chemin de la base de données de test."""
    db_path = test_data_dir / "test.db"
    yield db_path
    # Nettoyage après chaque test
    if db_path.exists():
        os.remove(db_path)

# Fixtures pour les modèles ML de test
@pytest.fixture(scope="session")
def test_models_dir(project_root: Path) -> Path:
    """Retourne le chemin du répertoire des modèles de test."""
    path = project_root / "tests" / "resources" / "ml_models"
    path.mkdir(parents=True, exist_ok=True)
    return path

# Fixtures pour la configuration de test
@pytest.fixture(scope="function")
def test_config():
    """Retourne une configuration de test."""
    from src.infrastructure.config import Config
    return Config(
        debug=True,
        env="test",
        ml={
            "embedding_model": "test-model",
            "chunk_size": 100,
            "chunk_overlap": 20
        },
        storage={
            "max_file_size": 1024 * 1024  # 1MB
        }
    )
