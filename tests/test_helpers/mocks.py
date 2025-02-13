"""Mocks réutilisables pour les tests."""
from unittest.mock import Mock
from typing import List, Optional
from src.domain.entities.document import Document
from src.domain.entities.document_chunk import DocumentChunk

class MockMLService:
    """Mock du service ML."""
    
    def __init__(self, embedding_size: int = 3):
        self.embedding_size = embedding_size
        self.chunk_text = Mock(return_value=["Chunk 1", "Chunk 2"])
        self.generate_embeddings = Mock(return_value=[0.1] * embedding_size)

class MockDocumentRepository:
    """Mock du repository de documents."""
    
    def __init__(self):
        self._documents: dict[str, Document] = {}
        self._chunks: dict[str, List[DocumentChunk]] = {}
        
    def save(self, document: Document) -> None:
        self._documents[document.id] = document
        
    def get_by_id(self, document_id: str) -> Optional[Document]:
        return self._documents.get(document_id)
        
    def save_chunks(self, chunks: List[DocumentChunk]) -> None:
        for chunk in chunks:
            if chunk.document_id not in self._chunks:
                self._chunks[chunk.document_id] = []
            self._chunks[chunk.document_id].append(chunk)
            
    def get_chunks(self, document_id: str) -> List[DocumentChunk]:
        return self._chunks.get(document_id, [])
