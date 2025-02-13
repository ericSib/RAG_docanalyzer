"""Service de gestion du stockage."""
from pathlib import Path
from typing import Optional, List
import shutil
import aiofiles
import aiofiles.os

from ..utils.logger import Logger
from ..core.document import Document
from ..data.repository import DocumentRepository, AnalysisRepository

class StorageService:
    """Service de gestion du stockage."""
    
    def __init__(
        self,
        documents_dir: Path,
        document_repo: DocumentRepository,
        analysis_repo: AnalysisRepository,
        logger: Optional[Logger] = None
    ):
        """Initialise le service.
        
        Args:
            documents_dir: Répertoire des documents
            document_repo: Repository des documents
            analysis_repo: Repository des analyses
            logger: Logger optionnel
        """
        self.documents_dir = documents_dir
        self.document_repo = document_repo
        self.analysis_repo = analysis_repo
        self.logger = logger or Logger()
    
    async def initialize(self) -> None:
        """Initialise le service."""
        self.logger.info("Initialisation du service de stockage...")
        
        # Crée le répertoire des documents si nécessaire
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialise les repositories
        await self.document_repo.connect()
        await self.analysis_repo.connect()
        
        self.logger.info("Service de stockage initialisé")
    
    async def save_document_file(self, file_path: Path) -> Document:
        """Sauvegarde un fichier document.
        
        Args:
            file_path: Chemin du fichier à sauvegarder
            
        Returns:
            Document créé
        """
        # Vérifie que le fichier existe
        if not file_path.exists():
            raise FileNotFoundError(f"Le fichier n'existe pas: {file_path}")
        
        # Copie le fichier dans le répertoire des documents
        target_path = self.documents_dir / file_path.name
        await self._copy_file(file_path, target_path)
        
        # Lit le contenu du fichier
        async with aiofiles.open(target_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # Crée et sauvegarde le document
        document = Document.create(
            path=target_path,
            name=target_path.name,
            content=content
        )
        await self.document_repo.save(document)
        
        self.logger.info(f"Document sauvegardé: {document.id}")
        return document
    
    async def delete_document(self, document_id: str) -> None:
        """Supprime un document.
        
        Args:
            document_id: ID du document à supprimer
        """
        # Récupère le document
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document non trouvé: {document_id}")
        
        # Supprime le fichier
        if document.path.exists():
            await aiofiles.os.remove(document.path)
        
        # Supprime les données
        await self.document_repo.delete(document_id)
        await self.analysis_repo.delete_by_document_id(document_id)
        
        self.logger.info(f"Document supprimé: {document_id}")
    
    async def _copy_file(self, src: Path, dst: Path) -> None:
        """Copie un fichier de manière asynchrone.
        
        Args:
            src: Chemin source
            dst: Chemin destination
        """
        async with aiofiles.open(src, 'rb') as fsrc:
            async with aiofiles.open(dst, 'wb') as fdst:
                await fdst.write(await fsrc.read())
