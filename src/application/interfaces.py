"""Interfaces pour l'inversion de dépendance."""
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from .domain import Document, AnalysisResult, DocumentChunk

class DocumentRepository(ABC):
    """Interface pour le stockage des documents."""
    
    @abstractmethod
    async def save(self, document: Document) -> None:
        """Sauvegarde un document."""
        pass
    
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Récupère un document par son ID."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Document]:
        """Liste tous les documents."""
        pass

class AnalysisRepository(ABC):
    """Interface pour le stockage des analyses."""
    
    @abstractmethod
    async def save(self, analysis: AnalysisResult) -> None:
        """Sauvegarde une analyse."""
        pass
    
    @abstractmethod
    async def get_by_document_id(self, document_id: str) -> Optional[AnalysisResult]:
        """Récupère l'analyse d'un document."""
        pass

class ModelService(ABC):
    """Interface pour la gestion des modèles."""
    
    @abstractmethod
    async def load_model(self, model_name: str) -> None:
        """Charge un modèle."""
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Calcule l'embedding d'un texte."""
        pass
    
    @abstractmethod
    async def chunk_text(self, text: str) -> List[DocumentChunk]:
        """Découpe un texte en chunks."""
        pass
