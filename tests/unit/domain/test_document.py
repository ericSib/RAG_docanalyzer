"""Tests unitaires pour les entités du domaine Document."""
import pytest
from datetime import datetime
from src.domain.entities.document import Document, DocumentStatus
from src.domain.entities.document_chunk import DocumentChunk

def test_document_creation():
    """Test la création d'un document."""
    doc = Document(
        id="test-1",
        name="test.txt",
        content="Test content",
        created_at=datetime.now(),
        status=DocumentStatus.PENDING
    )
    
    assert doc.id == "test-1"
    assert doc.name == "test.txt"
    assert doc.content == "Test content"
    assert doc.status == DocumentStatus.PENDING

def test_document_chunk_creation():
    """Test la création d'un chunk de document."""
    chunk = DocumentChunk(
        id="chunk-1",
        document_id="test-1",
        content="Test chunk",
        position=0,
        embedding=[0.1, 0.2, 0.3]
    )
    
    assert chunk.id == "chunk-1"
    assert chunk.document_id == "test-1"
    assert chunk.content == "Test chunk"
    assert chunk.position == 0
    assert len(chunk.embedding) == 3
