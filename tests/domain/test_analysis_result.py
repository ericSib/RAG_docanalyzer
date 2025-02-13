"""Tests pour l'entité AnalysisResult."""
import pytest
from datetime import datetime
from src.domain.entities.analysis_result import AnalysisResult
from src.domain.entities.document_chunk import DocumentChunk

def test_analysis_result_creation():
    """Test la création d'un résultat d'analyse."""
    # Arrange
    chunks = [
        DocumentChunk(
            id=f"chunk{i}",
            document_id="doc1",
            content=f"Chunk {i}",
            embedding=[0.1, 0.2, 0.3],
            position=i
        )
        for i in range(3)
    ]
    
    # Act
    analysis = AnalysisResult(
        id="analysis1",
        document_id="doc1",
        created_at=datetime.now(),
        summary="Test summary",
        metadata={},
        chunks=chunks
    )
    
    # Assert
    assert analysis.chunk_count == 3
    assert analysis.is_successful is True
    assert len(analysis.get_embeddings()) == 3
    assert len(analysis.get_chunk_contents()) == 3

def test_analysis_result_error_handling():
    """Test la gestion des erreurs d'analyse."""
    # Arrange
    analysis = AnalysisResult(
        id="analysis1",
        document_id="doc1",
        created_at=datetime.now(),
        summary="",
        metadata={},
        chunks=[],
        status="error",
        error_message="Test error"
    )
    
    # Assert
    assert analysis.is_successful is False
    assert analysis.chunk_count == 0

def test_analysis_result_chunk_retrieval():
    """Test la récupération des chunks."""
    # Arrange
    chunks = [
        DocumentChunk(
            id=f"chunk{i}",
            document_id="doc1",
            content=f"Chunk {i}",
            embedding=[0.1, 0.2, 0.3],
            position=i
        )
        for i in range(3)
    ]
    
    analysis = AnalysisResult(
        id="analysis1",
        document_id="doc1",
        created_at=datetime.now(),
        summary="Test summary",
        metadata={},
        chunks=chunks
    )
    
    # Act & Assert
    assert analysis.get_chunk_with_embedding(1) == chunks[1]
    assert analysis.get_chunk_with_embedding(5) is None
