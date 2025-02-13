"""Implémentation SQLite des repositories."""
import aiosqlite
from typing import List, Optional
from datetime import datetime
import json

from .repository import DocumentRepository, AnalysisRepository
from ..core.document import Document, AnalysisResult
from ..utils.logger import Logger

class SQLiteDocumentRepository(DocumentRepository):
    """Implémentation SQLite du DocumentRepository."""
    
    def __init__(self, db_path: str, logger: Logger):
        """Initialise le repository.
        
        Args:
            db_path: Chemin vers la base SQLite
            logger: Logger pour les événements
        """
        self.db_path = db_path
        self.logger = logger
        self.db = None
    
    async def connect(self) -> None:
        """Établit la connexion et crée les tables."""
        self.db = await aiosqlite.connect(self.db_path)
        await self._create_tables()
    
    async def disconnect(self) -> None:
        """Ferme la connexion."""
        if self.db:
            await self.db.close()
    
    async def _create_tables(self) -> None:
        """Crée les tables nécessaires."""
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    analyzed_at TIMESTAMP
                )
            """)
            await self.db.commit()
    
    async def save(self, document: Document) -> None:
        """Sauvegarde un document."""
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (id, path, name, content, created_at, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                document.id,
                str(document.path),
                document.name,
                document.content,
                document.created_at.isoformat(),
                document.analyzed_at.isoformat() if document.analyzed_at else None
            ))
            await self.db.commit()
            self.logger.info(f"Document sauvegardé: {document.id}")

class SQLiteAnalysisRepository(AnalysisRepository):
    """Implémentation SQLite du AnalysisRepository."""
    
    def __init__(self, db_path: str, logger: Logger):
        """Initialise le repository.
        
        Args:
            db_path: Chemin vers la base SQLite
            logger: Logger pour les événements
        """
        self.db_path = db_path
        self.logger = logger
        self.db = None
    
    async def connect(self) -> None:
        """Établit la connexion et crée les tables."""
        self.db = await aiosqlite.connect(self.db_path)
        await self._create_tables()
    
    async def disconnect(self) -> None:
        """Ferme la connexion."""
        if self.db:
            await self.db.close()
    
    async def _create_tables(self) -> None:
        """Crée les tables nécessaires."""
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    chunks TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                        ON DELETE CASCADE
                )
            """)
            await self.db.commit()
    
    async def save(self, analysis: AnalysisResult) -> None:
        """Sauvegarde une analyse."""
        chunks_json = json.dumps([{
            'id': c.id,
            'content': c.content,
            'embedding': c.embedding,
            'start_index': c.start_index,
            'end_index': c.end_index
        } for c in analysis.chunks])
        
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO analyses 
                (id, document_id, chunks, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                analysis.id,
                analysis.document_id,
                chunks_json,
                analysis.created_at.isoformat()
            ))
            await self.db.commit()
            self.logger.info(f"Analyse sauvegardée: {analysis.id}")
