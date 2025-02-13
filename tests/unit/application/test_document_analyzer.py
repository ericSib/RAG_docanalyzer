"""Tests unitaires pour le cas d'utilisation d'analyse de document."""
import pytest
from unittest.mock import Mock, patch
from src.application.use_cases.analyze_document import DocumentAnalyzer
from src.domain.entities.document import Document, DocumentStatus

@pytest.fixture
def mock_ml_service():
    service = Mock()
    service.generate_embeddings.return_value = [0.1, 0.2, 0.3]
    service.chunk_text.return_value = ["Chunk 1", "Chunk 2"]
    return service

@pytest.fixture
def mock_document_repository():
    repo = Mock()
    repo.save.return_value = None
    return repo

def test_analyze_document(mock_ml_service, mock_document_repository):
    """Test l'analyse d'un document."""
    # Arrange
    analyzer = DocumentAnalyzer(
        ml_service=mock_ml_service,
        document_repository=mock_document_repository
    )
    document = Document(
        id="test-1",
        name="test.txt",
        content="Test content",
        status=DocumentStatus.PENDING
    )

    # Act
    result = analyzer.analyze(document)

    # Assert
    assert result.status == DocumentStatus.COMPLETED
    assert mock_ml_service.chunk_text.called
    assert mock_ml_service.generate_embeddings.called
    assert mock_document_repository.save.called
