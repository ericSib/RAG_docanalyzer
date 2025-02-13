"""Modèle de document."""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import uuid

@dataclass
class DocumentChunk:
    """Chunk de document."""
    id: str
    content: str
    start_index: int
    end_index: int
    embedding: Optional[List[float]] = None

@dataclass
class Document:
    """Document analysé."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path: Path
    name: str
    content: str
    chunks: List[DocumentChunk] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, path: Path, name: str, content: str) -> 'Document':
        """Crée un nouveau document.
        
        Args:
            path: Chemin du fichier
            name: Nom du document
            content: Contenu du document
            
        Returns:
            Document créé
        """
        return cls(
            path=path,
            name=name,
            content=content
        )
