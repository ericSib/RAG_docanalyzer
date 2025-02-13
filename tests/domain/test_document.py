"""Tests pour l'entité Document."""
import pytest
from datetime import datetime
from src.domain.entities.document import Document
from src.domain.entities.document_chunk import DocumentChunk

def test_document_validation():
    """Test la validation d'un document."""
    # Arrange
    valid_doc = Document(
        id="1",
        name="test.txt",
        content="Test content",
        created_at=datetime.now(),
        analysis_status="pending",
        metadata={}
    )
    
    invalid_doc = Document(
        id="2",
        name="",
        content="",
        created_at=datetime.now(),
        analysis_status="pending",
        metadata={}
    )
    
    # Act & Assert
    assert valid_doc.validate() is True
    assert invalid_doc.validate() is False

def test_document_chunk_management():
    """Test la gestion des chunks d'un document."""
    # Arrange
    doc = Document(
        id="1",
        name="test.txt",
        content="Test content",
        created_at=datetime.now(),
        analysis_status="pending",
        metadata={}
    )
    
    chunk = DocumentChunk(
        id="chunk1",
        document_id=doc.id,
        content="Test chunk",
        embedding=[0.1, 0.2, 0.3],
        position=0
    )
    
    # Act
    doc.add_chunk(chunk)
    
    # Assert
    assert doc.chunk_count == 1
    assert doc.get_chunk_by_position(0) == chunk
    assert doc.get_chunk_by_position(1) is None

def test_document_analysis_status():
    """Test le statut d'analyse d'un document."""
    # Arrange
    doc = Document(
        id="1",
        name="test.txt",
        content="Test content",
        created_at=datetime.now(),
        analysis_status="pending",
        metadata={}
    )
    
    # Assert
    assert doc.is_analyzed is False
    
    # Act
    doc.analysis_status = "completed"
    
    # Assert
    assert doc.is_analyzed is True
