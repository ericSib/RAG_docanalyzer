"""Tests pour l'entité DocumentChunk."""
import pytest
from src.domain.entities.document_chunk import DocumentChunk

def test_document_chunk_creation():
    """Test la création d'un chunk."""
    # Arrange & Act
    chunk = DocumentChunk(
        id="chunk1",
        document_id="doc1",
        content="Test content",
        embedding=[0.1, 0.2, 0.3],
        position=0
    )
    
    # Assert
    assert len(chunk) == len("Test content")
    assert chunk.get_embedding_dimension() == 3

def test_document_chunk_empty_content():
    """Test un chunk avec contenu vide."""
    # Arrange & Act
    chunk = DocumentChunk(
        id="chunk1",
        document_id="doc1",
        content="",
        embedding=[0.1],
        position=0
    )
    
    # Assert
    assert len(chunk) == 0
    assert chunk.get_embedding_dimension() == 1
