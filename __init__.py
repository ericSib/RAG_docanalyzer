"""
RAG Document Analyzer
-------------------
Un système de RAG (Retrieval-Augmented Generation) pour l'analyse et la recherche de documents.
"""

from .core.config import settings
from .services.document_processor import DocumentProcessor
from .services.embedding_service import EmbeddingService
from .services.search_service import SearchService

__version__ = "0.1.0"
__author__ = "Votre Nom"

# Configuration du logging
from .core.logging import configure_logging
configure_logging()
