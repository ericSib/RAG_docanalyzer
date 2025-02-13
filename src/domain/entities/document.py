"""Document entity module."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from .document_chunk import DocumentChunk

@dataclass
class Document:
    """Entité document."""
    id: str
    name: str
    content: str
    created_at: datetime
    analysis_status: str
    metadata: Dict[str, Any]
    chunks: Optional[List[DocumentChunk]] = None

    def validate(self) -> bool:
        """Valide l'intégrité du document."""
        return bool(self.content and self.name)

    @property
    def chunk_count(self) -> int:
        """Retourne le nombre de chunks."""
        return len(self.chunks) if self.chunks else 0

    @property
    def is_analyzed(self) -> bool:
        """Vérifie si le document a été analysé."""
        return self.analysis_status == "completed"

    def add_chunk(self, chunk: DocumentChunk) -> None:
        """Ajoute un chunk au document."""
        if self.chunks is None:
            self.chunks = []
        self.chunks.append(chunk)

    def get_chunk_by_position(self, position: int) -> Optional[DocumentChunk]:
        """Récupère un chunk par sa position."""
        if not self.chunks:
            return None
        return next((chunk for chunk in self.chunks if chunk.position == position), None)
