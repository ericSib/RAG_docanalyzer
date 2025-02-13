"""Interfaces des repositories."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..core.document import Document

class DocumentRepository(ABC):
    """Interface du repository de documents."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Établit la connexion."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme la connexion."""
        pass
    
    @abstractmethod
    async def save(self, document: Document) -> bool:
        """Sauvegarde un document.
        
        Args:
            document: Document à sauvegarder
            
        Returns:
            True si succès
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """Récupère un document par son ID.
        
        Args:
            doc_id: ID du document
            
        Returns:
            Document ou None
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Document]:
        """Récupère tous les documents.
        
        Returns:
            Liste des documents
        """
        pass
    
    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """Supprime un document.
        
        Args:
            doc_id: ID du document
            
        Returns:
            True si succès
        """
        pass
    
    @abstractmethod
    async def update(self, document: Document) -> bool:
        """Met à jour un document.
        
        Args:
            document: Document à mettre à jour
            
        Returns:
            True si succès
        """
        pass

class AnalysisRepository(ABC):
    """Interface du repository d'analyses."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Établit la connexion."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme la connexion."""
        pass
    
    @abstractmethod
    async def save_analysis(
        self,
        document_id: str,
        chunks: List[dict],
        embeddings: List[List[float]],
        created_at: datetime = None
    ) -> str:
        """Sauvegarde une analyse.
        
        Args:
            document_id: ID du document analysé
            chunks: Liste des chunks
            embeddings: Liste des embeddings
            created_at: Date de création
            
        Returns:
            ID de l'analyse
        """
        pass
    
    @abstractmethod
    async def get_analysis(self, analysis_id: str) -> Optional[dict]:
        """Récupère une analyse par son ID.
        
        Args:
            analysis_id: ID de l'analyse
            
        Returns:
            Analyse ou None
        """
        pass
    
    @abstractmethod
    async def delete_by_document_id(self, document_id: str) -> bool:
        """Supprime les analyses d'un document.
        
        Args:
            document_id: ID du document
            
        Returns:
            True si succès
        """
        pass
