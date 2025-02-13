"""Analysis result entity module."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any
from .document_chunk import DocumentChunk

@dataclass
class AnalysisResult:
    """Représente le résultat d'une analyse de document."""
    id: str
    document_id: str
    created_at: datetime
    summary: str
    metadata: Dict[str, Any]
    chunks: List[DocumentChunk]
    status: str = "completed"
    error_message: str = None

    @property
    def chunk_count(self) -> int:
        """Retourne le nombre de chunks."""
        return len(self.chunks)

    @property
    def is_successful(self) -> bool:
        """Vérifie si l'analyse s'est terminée avec succès."""
        return self.status == "completed" and not self.error_message

    def get_embeddings(self) -> List[List[float]]:
        """Retourne tous les embeddings."""
        return [chunk.embedding for chunk in self.chunks]

    def get_chunk_contents(self) -> List[str]:
        """Retourne le contenu de tous les chunks."""
        return [chunk.content for chunk in self.chunks]

    def get_chunk_with_embedding(self, position: int) -> DocumentChunk:
        """Retourne un chunk spécifique."""
        return next((chunk for chunk in self.chunks if chunk.position == position), None)
