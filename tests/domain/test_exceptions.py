"""Tests pour les exceptions du domaine."""
import pytest
from src.domain.exceptions import (
    DocumentNotFoundError,
    DocumentValidationError,
    AnalysisNotFoundError,
    AnalysisFailedError,
    ModelNotFoundError,
    ModelDownloadError,
    DatabaseError,
    FileSystemError,
    ConfigurationError
)

def test_document_not_found_error():
    """Test l'exception DocumentNotFoundError."""
    # Act
    error = DocumentNotFoundError("doc123")
    
    # Assert
    assert error.code == "DOCUMENT_NOT_FOUND"
    assert "doc123" in str(error)

def test_document_validation_error():
    """Test l'exception DocumentValidationError."""
    # Act
    error = DocumentValidationError("contenu vide")
    
    # Assert
    assert error.code == "DOCUMENT_VALIDATION_ERROR"
    assert "contenu vide" in str(error)

def test_analysis_not_found_error():
    """Test l'exception AnalysisNotFoundError."""
    # Act
    error = AnalysisNotFoundError("analysis123")
    
    # Assert
    assert error.code == "ANALYSIS_NOT_FOUND"
    assert "analysis123" in str(error)

def test_analysis_failed_error():
    """Test l'exception AnalysisFailedError."""
    # Act
    error = AnalysisFailedError("erreur modèle", "doc123")
    
    # Assert
    assert error.code == "ANALYSIS_FAILED"
    assert "erreur modèle" in str(error)
    assert "doc123" in str(error)

def test_model_not_found_error():
    """Test l'exception ModelNotFoundError."""
    # Act
    error = ModelNotFoundError("fr_core_news_md")
    
    # Assert
    assert error.code == "MODEL_NOT_FOUND"
    assert "fr_core_news_md" in str(error)

def test_model_download_error():
    """Test l'exception ModelDownloadError."""
    # Act
    error = ModelDownloadError("fr_core_news_md", "réseau indisponible")
    
    # Assert
    assert error.code == "MODEL_DOWNLOAD_ERROR"
    assert "fr_core_news_md" in str(error)
    assert "réseau indisponible" in str(error)

def test_database_error():
    """Test l'exception DatabaseError."""
    # Act
    error = DatabaseError("insertion", "contrainte unique violée")
    
    # Assert
    assert error.code == "DATABASE_ERROR"
    assert "insertion" in str(error)
    assert "contrainte unique violée" in str(error)

def test_filesystem_error():
    """Test l'exception FileSystemError."""
    # Act
    error = FileSystemError("lecture", "/test/file.txt", "permission refusée")
    
    # Assert
    assert error.code == "FILESYSTEM_ERROR"
    assert "lecture" in str(error)
    assert "/test/file.txt" in str(error)
    assert "permission refusée" in str(error)

def test_configuration_error():
    """Test l'exception ConfigurationError."""
    # Act
    error = ConfigurationError("DB_PATH", "chemin invalide")
    
    # Assert
    assert error.code == "CONFIGURATION_ERROR"
    assert "DB_PATH" in str(error)
    assert "chemin invalide" in str(error)

def test_exception_inheritance():
    """Test l'héritage des exceptions."""
    # Arrange & Act
    doc_error = DocumentNotFoundError("doc123")
    analysis_error = AnalysisFailedError("erreur")
    model_error = ModelNotFoundError("model123")
    storage_error = DatabaseError("select", "erreur")
    config_error = ConfigurationError("setting", "erreur")
    
    # Assert
    from src.domain.exceptions import DomainException
    assert isinstance(doc_error, DomainException)
    assert isinstance(analysis_error, DomainException)
    assert isinstance(model_error, DomainException)
    assert isinstance(storage_error, DomainException)
    assert isinstance(config_error, DomainException)
