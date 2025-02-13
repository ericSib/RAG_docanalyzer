"""Domain layer package."""
from .entities.document import Document
from .entities.analysis_result import AnalysisResult
from .interfaces.repositories import DocumentRepository, AnalysisRepository
from .interfaces.services import TextProcessor, EmbeddingService, ModelManager
from .exceptions import (
    DomainException,
    DocumentNotFoundError,
    DocumentValidationError,
    AnalysisNotFoundError,
    AnalysisFailedError,
    ModelNotFoundError,
    ModelDownloadError,
    DatabaseError,
    FileSystemError,
    ConfigurationError
)

__all__ = [
    # Entities
    'Document',
    'AnalysisResult',
    # Interfaces
    'DocumentRepository',
    'AnalysisRepository',
    'TextProcessor',
    'EmbeddingService',
    'ModelManager',
    # Exceptions
    'DomainException',
    'DocumentNotFoundError',
    'DocumentValidationError',
    'AnalysisNotFoundError',
    'AnalysisFailedError',
    'ModelNotFoundError',
    'ModelDownloadError',
    'DatabaseError',
    'FileSystemError',
    'ConfigurationError'
]
