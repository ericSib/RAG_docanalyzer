"""Document chunk entity module."""
from dataclasses import dataclass
from typing import List

@dataclass
class DocumentChunk:
    """Représente un fragment de document."""
    id: str
    document_id: str
    content: str
    embedding: List[float]
    position: int
    
    def __len__(self) -> int:
        """Retourne la longueur du contenu."""
        return len(self.content)

    def get_embedding_dimension(self) -> int:
        """Retourne la dimension de l'embedding."""
        return len(self.embedding)
