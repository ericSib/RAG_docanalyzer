"""Factories pour la création d'objets de test."""
from datetime import datetime
from src.domain.entities.document import Document, DocumentStatus
from src.domain.entities.document_chunk import DocumentChunk

class DocumentFactory:
    """Factory pour créer des documents de test."""
    
    @staticmethod
    def create(
        id: str = "test-doc-1",
        name: str = "test.txt",
        content: str = "Test content",
        status: DocumentStatus = DocumentStatus.PENDING
    ) -> Document:
        """Crée un document de test."""
        return Document(
            id=id,
            name=name,
            content=content,
            created_at=datetime.now(),
            status=status
        )

class DocumentChunkFactory:
    """Factory pour créer des chunks de test."""
    
    @staticmethod
    def create(
        id: str = "test-chunk-1",
        document_id: str = "test-doc-1",
        content: str = "Test chunk content",
        position: int = 0,
        embedding: list[float] = None
    ) -> DocumentChunk:
        """Crée un chunk de test."""
        if embedding is None:
            embedding = [0.1, 0.2, 0.3]
            
        return DocumentChunk(
            id=id,
            document_id=document_id,
            content=content,
            position=position,
            embedding=embedding
        )
