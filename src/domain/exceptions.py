"""Exceptions du domaine."""
from typing import Optional

class DomainException(Exception):
    """Exception de base pour le domaine."""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)

class DocumentError(DomainException):
    """Erreurs liées aux documents."""
    pass

class DocumentNotFoundError(DocumentError):
    """Document non trouvé."""
    
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document non trouvé: {document_id}",
            code="DOCUMENT_NOT_FOUND"
        )

class DocumentValidationError(DocumentError):
    """Erreur de validation de document."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Document invalide: {reason}",
            code="DOCUMENT_VALIDATION_ERROR"
        )

class AnalysisError(DomainException):
    """Erreurs liées à l'analyse."""
    pass

class AnalysisNotFoundError(AnalysisError):
    """Analyse non trouvée."""
    
    def __init__(self, analysis_id: str):
        super().__init__(
            message=f"Analyse non trouvée: {analysis_id}",
            code="ANALYSIS_NOT_FOUND"
        )

class AnalysisFailedError(AnalysisError):
    """Échec de l'analyse."""
    
    def __init__(self, reason: str, document_id: Optional[str] = None):
        message = f"Échec de l'analyse: {reason}"
        if document_id:
            message += f" (document: {document_id})"
        super().__init__(message=message, code="ANALYSIS_FAILED")

class ModelError(DomainException):
    """Erreurs liées aux modèles."""
    pass

class ModelNotFoundError(ModelError):
    """Modèle non trouvé."""
    
    def __init__(self, model_name: str):
        super().__init__(
            message=f"Modèle non trouvé: {model_name}",
            code="MODEL_NOT_FOUND"
        )

class ModelDownloadError(ModelError):
    """Erreur de téléchargement de modèle."""
    
    def __init__(self, model_name: str, reason: str):
        super().__init__(
            message=f"Erreur lors du téléchargement du modèle {model_name}: {reason}",
            code="MODEL_DOWNLOAD_ERROR"
        )

class StorageError(DomainException):
    """Erreurs liées au stockage."""
    pass

class DatabaseError(StorageError):
    """Erreur de base de données."""
    
    def __init__(self, operation: str, details: str):
        super().__init__(
            message=f"Erreur de base de données lors de {operation}: {details}",
            code="DATABASE_ERROR"
        )

class FileSystemError(StorageError):
    """Erreur du système de fichiers."""
    
    def __init__(self, operation: str, path: str, details: str):
        super().__init__(
            message=f"Erreur système lors de {operation} sur {path}: {details}",
            code="FILESYSTEM_ERROR"
        )

class ConfigurationError(DomainException):
    """Erreurs de configuration."""
    
    def __init__(self, setting: str, reason: str):
        super().__init__(
            message=f"Erreur de configuration pour {setting}: {reason}",
            code="CONFIGURATION_ERROR"
        )
