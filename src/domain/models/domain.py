"""Modèles de domaine pour l'application."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List

@dataclass
class Document:
    """Document à analyser."""
    id: str
    path: Path
    name: str
    content: str
    created_at: datetime
    analyzed_at: Optional[datetime] = None
    
@dataclass
class AnalysisResult:
    """Résultat d'analyse d'un document."""
    id: str
    document_id: str
    chunks: List['DocumentChunk']
    created_at: datetime
    
@dataclass
class DocumentChunk:
    """Chunk de document avec son embedding."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    start_index: int = 0
    end_index: int = 0
