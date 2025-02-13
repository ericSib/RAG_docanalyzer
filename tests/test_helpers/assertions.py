"""Assertions personnalisées pour les tests."""
from typing import List
import numpy as np
from src.domain.entities.document import Document
from src.domain.entities.document_chunk import DocumentChunk

def assert_document_valid(document: Document) -> None:
    """Vérifie qu'un document est valide."""
    assert document.id is not None
    assert document.name is not None
    assert document.content is not None
    assert document.created_at is not None
    assert document.status is not None

def assert_chunks_valid(chunks: List[DocumentChunk], document_id: str) -> None:
    """Vérifie que les chunks sont valides."""
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.id is not None
        assert chunk.document_id == document_id
        assert chunk.content is not None
        assert isinstance(chunk.position, int)
        assert chunk.position >= 0
        assert_embedding_valid(chunk.embedding)

def assert_embedding_valid(embedding: List[float]) -> None:
    """Vérifie qu'un embedding est valide."""
    assert embedding is not None
    assert len(embedding) > 0
    assert all(isinstance(x, (float, np.float32)) for x in embedding)
    assert not any(np.isnan(x) for x in embedding)
