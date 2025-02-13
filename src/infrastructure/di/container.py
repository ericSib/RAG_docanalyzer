"""Dependency injection container module."""
from pathlib import Path
from dependency_injector import containers, providers
from ...domain.interfaces.repositories import (
    DocumentRepository, 
    AnalysisRepository,
    ChunkRepository
)
from ...domain.interfaces.services import (
    AnalyzerService,
    TextExtractor,
    ModelService,
    SearchService
)
from ...application.use_cases.analyze_document import AnalyzeDocumentUseCase
from ...application.use_cases.manage_models import ManageModelsUseCase
from ..persistence.sqlite.repositories import (
    SQLiteDocumentRepository,
    SQLiteAnalysisRepository,
    SQLiteChunkRepository
)
from ..services.analyzer import SpacyAnalyzerService
from ..services.text import TextExtractorService
from ..services.models import HuggingFaceModelService
from ..services.search import EmbeddingSearchService
from ...config.settings import settings

class Container(containers.DeclarativeContainer):
    """Conteneur d'injection de dépendances."""
    
    # Configuration
    config = providers.Configuration()
    
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.presentation.qt",
            "src.presentation.viewmodels"
        ]
    )

    # Services
    text_extractor = providers.Singleton(
        TextExtractorService
    )

    model_service = providers.Singleton(
        HuggingFaceModelService,
        models_dir=settings.models_dir
    )

    analyzer_service = providers.Singleton(
        SpacyAnalyzerService,
        model_service=model_service
    )

    search_service = providers.Singleton(
        EmbeddingSearchService,
        model_service=model_service
    )

    # Repositories
    document_repository = providers.Singleton(
        SQLiteDocumentRepository,
        database_path=settings.db_path
    )

    analysis_repository = providers.Singleton(
        SQLiteAnalysisRepository,
        database_path=settings.db_path
    )

    chunk_repository = providers.Singleton(
        SQLiteChunkRepository,
        database_path=settings.db_path
    )

    # Use Cases
    analyze_document = providers.Factory(
        AnalyzeDocumentUseCase,
        document_repository=document_repository,
        analysis_repository=analysis_repository,
        chunk_repository=chunk_repository,
        analyzer_service=analyzer_service,
        text_extractor=text_extractor
    )

    manage_models = providers.Factory(
        ManageModelsUseCase,
        model_service=model_service
    )
