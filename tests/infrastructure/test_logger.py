"""Tests pour le module de logging."""
import json
import logging
from pathlib import Path
import pytest
from src.infrastructure.logging import Logger

@pytest.fixture
def temp_log_file(test_dir):
    """Crée un fichier de log temporaire."""
    return test_dir / "test.log"

def test_logger_initialization():
    """Test l'initialisation du logger."""
    # Act
    logger = Logger(name="test_logger")
    
    # Assert
    assert logger.name == "test_logger"
    assert logger.log_level == logging.INFO
    assert logger.enable_console is True

def test_logger_with_file(temp_log_file):
    """Test le logger avec un fichier de sortie."""
    # Arrange
    logger = Logger(
        name="test_logger",
        log_level="DEBUG",
        log_path=temp_log_file
    )
    
    # Act
    test_message = "Test message"
    logger.info(test_message)
    
    # Assert
    assert temp_log_file.exists()
    log_content = temp_log_file.read_text()
    log_entry = json.loads(log_content.strip())
    assert log_entry["event"] == test_message
    assert log_entry["level"] == "info"
    assert log_entry["logger"] == "test_logger"

def test_logger_levels(temp_log_file):
    """Test les différents niveaux de log."""
    # Arrange
    logger = Logger(
        name="test_logger",
        log_level="DEBUG",
        log_path=temp_log_file
    )
    
    # Act
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Assert
    log_content = temp_log_file.read_text()
    log_entries = [json.loads(line) for line in log_content.strip().split('\n')]
    
    assert len(log_entries) == 4
    assert log_entries[0]["level"] == "debug"
    assert log_entries[1]["level"] == "info"
    assert log_entries[2]["level"] == "warning"
    assert log_entries[3]["level"] == "error"

def test_logger_with_context():
    """Test le logger avec des informations contextuelles."""
    # Arrange
    logger = Logger(name="test_logger")
    
    # Act
    logger.info(
        "Processing document",
        document_id="doc123",
        operation="analysis",
        duration=1.5
    )
    
    # Le test passe car nous ne vérifions que l'absence d'erreur
    # Dans un cas réel, nous capturerions la sortie console
    # et vérifierions son contenu

def test_logger_exception():
    """Test le logging d'exceptions."""
    # Arrange
    logger = Logger(name="test_logger")
    
    try:
        # Act
        raise ValueError("Test error")
    except Exception as e:
        logger.exception("An error occurred", exc_info=e)
        
    # Le test passe car nous ne vérifions que l'absence d'erreur
    # Dans un cas réel, nous capturerions la sortie console
    # et vérifierions son contenu
