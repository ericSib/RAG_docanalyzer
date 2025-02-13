"""Tests pour les modèles de domaine."""
import pytest
from datetime import datetime
from pathlib import Path

from src.core.domain import Document, AnalysisResult, DocumentChunk

def test_document_creation():
    """Test la création d'un document."""
    # Arrange
    doc_id = "doc123"
    path = Path("/test/doc.txt")
    name = "doc.txt"
    content = "Test content"
    created_at = datetime.now()
    
    # Act
    doc = Document(
        id=doc_id,
        path=path,
        name=name,
        content=content,
        created_at=created_at
    )
    
    # Assert
    assert doc.id == doc_id
    assert doc.path == path
    assert doc.name == name
    assert doc.content == content
    assert doc.created_at == created_at
    assert doc.analyzed_at is None

def test_analysis_result_creation():
    """Test la création d'un résultat d'analyse."""
    # Arrange
    analysis_id = "analysis123"
    doc_id = "doc123"
    chunks = [
        DocumentChunk(
            id="chunk1",
            content="Test chunk 1",
            start_index=0,
            end_index=10
        ),
        DocumentChunk(
            id="chunk2",
            content="Test chunk 2",
            start_index=11,
            end_index=20
        )
    ]
    created_at = datetime.now()
    
    # Act
    analysis = AnalysisResult(
        id=analysis_id,
        document_id=doc_id,
        chunks=chunks,
        created_at=created_at
    )
    
    # Assert
    assert analysis.id == analysis_id
    assert analysis.document_id == doc_id
    assert len(analysis.chunks) == 2
    assert analysis.created_at == created_at

def test_document_chunk_creation():
    """Test la création d'un chunk de document."""
    # Arrange
    chunk_id = "chunk123"
    content = "Test content"
    embedding = [0.1, 0.2, 0.3]
    start_index = 0
    end_index = 10
    
    # Act
    chunk = DocumentChunk(
        id=chunk_id,
        content=content,
        embedding=embedding,
        start_index=start_index,
        end_index=end_index
    )
    
    # Assert
    assert chunk.id == chunk_id
    assert chunk.content == content
    assert chunk.embedding == embedding
    assert chunk.start_index == start_index
    assert chunk.end_index == end_index
