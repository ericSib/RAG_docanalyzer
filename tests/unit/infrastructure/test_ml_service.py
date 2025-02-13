"""Tests unitaires pour le service ML."""
import pytest
import numpy as np
from src.infrastructure.ml_service import MLService
from src.infrastructure.config import Config

@pytest.fixture
def ml_service(test_config, test_models_dir):
    """Crée une instance de MLService pour les tests."""
    return MLService(
        model_path=test_models_dir / "test_model",
        config=test_config
    )

def test_chunk_text(ml_service):
    """Test le découpage de texte en chunks."""
    text = "Ceci est un long texte. " * 10
    chunks = ml_service.chunk_text(text)
    
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) <= ml_service.config.ml.chunk_size for chunk in chunks)

def test_generate_embeddings(ml_service):
    """Test la génération d'embeddings."""
    text = "Ceci est un test."
    embedding = ml_service.generate_embeddings(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.ndim == 1  # Vecteur 1D
    assert not np.isnan(embedding).any()  # Pas de NaN
