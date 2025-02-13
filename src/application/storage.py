"""Module de gestion du stockage local des documents et analyses."""
import sqlite3
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
from .config import config

class LocalStorage:
    def __init__(self):
        self.db_path = config.app_dir / 'storage.db'
        self._init_database()

    def _init_database(self):
        """Initialise la base de données SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    chunks TEXT,
                    embeddings TEXT,
                    summary TEXT,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')

    def add_document(self, file_path: str, content: str, metadata: Dict = None) -> int:
        """Ajoute un nouveau document à la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO documents (filename, file_path, content, metadata) VALUES (?, ?, ?, ?)',
                (Path(file_path).name, file_path, content, json.dumps(metadata or {}))
            )
            return cursor.lastrowid

    def add_analysis(self, document_id: int, chunks: List[str], embeddings: List[List[float]], 
                    summary: str) -> int:
        """Ajoute une nouvelle analyse à la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO analyses (document_id, chunks, embeddings, summary) VALUES (?, ?, ?, ?)',
                (document_id, json.dumps(chunks), json.dumps(embeddings), summary)
            )
            return cursor.lastrowid

    def get_document(self, document_id: int) -> Optional[Dict]:
        """Récupère un document par son ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """Récupère une analyse par son ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_recent_documents(self, limit: int = 10) -> List[Dict]:
        """Récupère les documents récents."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM documents ORDER BY created_at DESC LIMIT ?',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def search_documents(self, query: str) -> List[Dict]:
        """Recherche dans les documents."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM documents 
                   WHERE filename LIKE ? OR content LIKE ?
                   ORDER BY created_at DESC''',
                (f'%{query}%', f'%{query}%')
            )
            return [dict(row) for row in cursor.fetchall()]

# Instance unique du stockage
storage = LocalStorage()
