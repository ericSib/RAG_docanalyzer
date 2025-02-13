"""Repository interfaces module."""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.document import Document
from ..entities.analysis_result import AnalysisResult
from ..entities.document_chunk import DocumentChunk

class DocumentRepository(ABC):
    """Interface pour le stockage des documents."""
    
    @abstractmethod
    async def save(self, document: Document) -> bool:
        """Sauvegarde un document."""
        pass

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Récupère un document par son ID."""
        pass

    @abstractmethod
    async def get_recent(self, limit: int = 10) -> List[Document]:
        """Récupère les documents récents."""
        pass

    @abstractmethod
    async def search(self, query: str) -> List[Document]:
        """Recherche dans les documents."""
        pass

    @abstractmethod
    async def update_status(self, document_id: str, status: str) -> bool:
        """Met à jour le statut d'un document."""
        pass

class AnalysisRepository(ABC):
    """Interface pour le stockage des analyses."""
    
    @abstractmethod
    async def save(self, analysis: AnalysisResult) -> bool:
        """Sauvegarde une analyse."""
        pass

    @abstractmethod
    async def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Récupère une analyse par son ID."""
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: str) -> List[AnalysisResult]:
        """Récupère les analyses d'un document."""
        pass

    @abstractmethod
    async def get_latest_by_document_id(self, document_id: str) -> Optional[AnalysisResult]:
        """Récupère la dernière analyse d'un document."""
        pass

class ChunkRepository(ABC):
    """Interface pour le stockage des chunks."""
    
    @abstractmethod
    async def save_many(self, chunks: List[DocumentChunk]) -> bool:
        """Sauvegarde plusieurs chunks."""
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        """Récupère tous les chunks d'un document."""
        pass

    @abstractmethod
    async def search_similar(self, embedding: List[float], limit: int = 5) -> List[DocumentChunk]:
        """Recherche les chunks similaires."""
        pass
