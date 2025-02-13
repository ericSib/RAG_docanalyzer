"""Tests d'intégration pour le flux complet d'analyse de document."""
import pytest
from pathlib import Path
from src.domain.entities.document import Document, DocumentStatus
from src.application.use_cases.analyze_document import DocumentAnalyzer
from src.infrastructure.ml_service import MLService
from src.infrastructure.repository import DocumentRepository

def test_complete_document_analysis_flow(
    test_config,
    test_db_path,
    test_models_dir,
    test_documents_dir
):
    """Test le flux complet d'analyse d'un document."""
    # Arrange
    ml_service = MLService(
        model_path=test_models_dir / "test_model",
        config=test_config
    )
    document_repository = DocumentRepository(db_path=test_db_path)
    analyzer = DocumentAnalyzer(
        ml_service=ml_service,
        document_repository=document_repository
    )
    
    # Création d'un document test
    document = Document(
        id="test-integration-1",
        name="test.txt",
        content="Ceci est un document de test pour l'intégration.",
        status=DocumentStatus.PENDING
    )
    
    # Act
    document_repository.save(document)
    result = analyzer.analyze(document)
    saved_document = document_repository.get_by_id(document.id)
    
    # Assert
    assert result.status == DocumentStatus.COMPLETED
    assert saved_document is not None
    assert saved_document.status == DocumentStatus.COMPLETED
    # Vérifier que les chunks ont été créés
    chunks = document_repository.get_chunks(document.id)
    assert len(chunks) > 0
    assert all(chunk.embedding is not None for chunk in chunks)
