"""Document analysis use case module."""
from typing import Optional
from ...domain.interfaces.repositories import DocumentRepository, AnalysisRepository, ChunkRepository
from ...domain.interfaces.services import AnalyzerService, TextExtractor
from ...domain.entities.document import Document
from ...domain.entities.analysis_result import AnalysisResult
from ..interfaces.dto import AnalysisRequestDTO, AnalysisResultDTO

class AnalyzeDocumentUseCase:
    """Cas d'utilisation pour l'analyse de documents."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        analysis_repository: AnalysisRepository,
        chunk_repository: ChunkRepository,
        analyzer_service: AnalyzerService,
        text_extractor: TextExtractor
    ):
        self.document_repository = document_repository
        self.analysis_repository = analysis_repository
        self.chunk_repository = chunk_repository
        self.analyzer_service = analyzer_service
        self.text_extractor = text_extractor

    async def execute(self, document_id: str) -> Optional[AnalysisResultDTO]:
        """Exécute l'analyse d'un document."""
        # Récupération du document
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            return None

        try:
            # Mise à jour du statut
            await self.document_repository.update_status(document_id, "analyzing")

            # Analyse du document
            analysis_result = await self.analyzer_service.analyze(document)

            # Sauvegarde des chunks
            await self.chunk_repository.save_many(analysis_result.chunks)

            # Sauvegarde de l'analyse
            await self.analysis_repository.save(analysis_result)

            # Mise à jour du statut du document
            await self.document_repository.update_status(document_id, "completed")

            # Création du DTO
            return AnalysisResultDTO(
                id=analysis_result.id,
                document_id=analysis_result.document_id,
                summary=analysis_result.summary,
                chunk_count=analysis_result.chunk_count,
                created_at=analysis_result.created_at
            )

        except Exception as e:
            # En cas d'erreur, mise à jour du statut
            await self.document_repository.update_status(document_id, "error")
            raise e
