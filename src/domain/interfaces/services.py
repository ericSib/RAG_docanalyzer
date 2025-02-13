"""Service interfaces module."""
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from ..entities.document import Document
from ..entities.analysis_result import AnalysisResult
from ..entities.document_chunk import DocumentChunk

class AnalyzerService(ABC):
    """Interface pour l'analyse de documents."""
    
    @abstractmethod
    async def analyze(self, document: Document) -> AnalysisResult:
        """Analyse un document."""
        pass

    @abstractmethod
    async def create_chunks(self, content: str, chunk_size: int, 
                          chunk_overlap: int) -> List[str]:
        """Crée des chunks à partir du contenu."""
        pass

    @abstractmethod
    async def create_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Crée des embeddings pour les chunks."""
        pass

class TextExtractor(ABC):
    """Interface pour l'extraction de texte."""
    
    @abstractmethod
    async def extract_text(self, file_path: Path) -> str:
        """Extrait le texte d'un fichier."""
        pass

    @abstractmethod
    async def validate_file(self, file_path: Path) -> bool:
        """Valide un fichier."""
        pass

class ModelService(ABC):
    """Interface pour la gestion des modèles."""
    
    @abstractmethod
    async def ensure_models_available(self) -> bool:
        """S'assure que tous les modèles sont disponibles."""
        pass

    @abstractmethod
    async def get_model_info(self, model_name: str) -> dict:
        """Récupère les informations d'un modèle."""
        pass

    @abstractmethod
    async def download_model(self, model_name: str) -> bool:
        """Télécharge un modèle."""
        pass

class SearchService(ABC):
    """Interface pour la recherche."""
    
    @abstractmethod
    async def search_similar_chunks(self, query: str, 
                                  limit: int = 5) -> List[DocumentChunk]:
        """Recherche les chunks similaires à une requête."""
        pass

    @abstractmethod
    async def rank_documents(self, query: str, 
                           documents: List[Document]) -> List[Document]:
        """Classe les documents par pertinence."""
        pass
