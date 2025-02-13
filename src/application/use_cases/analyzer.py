"""Analyseur de documents."""
from typing import Dict, List, Optional
from pathlib import Path

from .document import Document, DocumentChunk
from ..services.ml_service import MLService
from ..utils.logger import Logger

class DocumentAnalyzer:
    """Analyseur de documents."""
    
    def __init__(
        self,
        ml_service: MLService,
        logger: Optional[Logger] = None
    ):
        """Initialise l'analyseur.
        
        Args:
            ml_service: Service ML pour l'analyse
            logger: Logger optionnel
        """
        self.ml_service = ml_service
        self.logger = logger or Logger()
    
    async def analyze(self, document: Document) -> Dict:
        """Analyse un document.
        
        Args:
            document: Document à analyser
            
        Returns:
            Résultats de l'analyse
        """
        self.logger.info(f"Analyse du document: {document.name}")
        
        try:
            # Découpage en chunks
            chunks = await self.ml_service.chunk_text(document.content)
            document.chunks = chunks
            
            # Génération des embeddings
            for chunk in chunks:
                chunk.embedding = await self.ml_service.get_embedding(chunk.content)
            
            # Analyse du document
            results = {
                'document_id': document.id,
                'chunks_count': len(chunks),
                'average_chunk_size': sum(len(c.content) for c in chunks) / len(chunks),
                'chunks': [
                    {
                        'id': c.id,
                        'content': c.content[:100] + '...' if len(c.content) > 100 else c.content,
                        'size': len(c.content)
                    }
                    for c in chunks
                ]
            }
            
            self.logger.info(f"Analyse terminée: {len(chunks)} chunks générés")
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse: {e}")
            raise

# Instance unique de l'analyseur
analyzer = DocumentAnalyzer(ml_service=MLService(), logger=Logger())
