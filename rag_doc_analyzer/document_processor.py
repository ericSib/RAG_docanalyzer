from typing import List, Dict, Any
from sqlalchemy.orm import Session
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from .models import Document, DocumentChunk

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.nlp = spacy.load('fr_core_news_md')
            logger.info("DocumentProcessor initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur initialisation DocumentProcessor: {str(e)}")
            raise
    
    def process_document(self, content: str, title: str = None) -> Dict[str, Any]:
        """Traite un document et stocke en base de données."""
        logger.info(f"Traitement document: {title}")
        
        try:
            # Analyse du texte et génération des chunks
            doc = self.nlp(content)
            chunks = self._generate_chunks(doc)
            
            # Génération des embeddings
            doc_embedding = self.model.encode(content)
            chunk_embeddings = self.model.encode(chunks)
            
            # Création et stockage du document
            document = Document(
                title=title or "Sans titre",
                content=content
            )
            document.set_embedding(doc_embedding)
            
            # Ajout à la session
            self.db_session.add(document)
            self.db_session.flush()
            
            # Création et stockage des chunks
            for chunk, emb in zip(chunks, chunk_embeddings):
                chunk_doc = DocumentChunk(
                    document_id=document.id,
                    content=chunk
                )
                chunk_doc.set_embedding(emb)
                self.db_session.add(chunk_doc)
            
            # Commit des changements
            self.db_session.commit()
            
            logger.info(f"Document traité avec succès: {document.id}")
            
            return {
                'id': document.id,
                'title': document.title,
                'content': document.content,
                'chunks': chunks,
                'embeddings': chunk_embeddings.tolist()
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Erreur traitement document: {str(e)}")
            raise
    
    def _generate_chunks(self, doc) -> List[str]:
        """Découpe le document en chunks intelligents."""
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sent in doc.sents:
            sent_length = len(sent.text.split())
            
            if current_length + sent_length > 512:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sent.text]
                current_length = sent_length
            else:
                current_chunk.append(sent.text)
                current_length += sent_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Effectue une recherche sémantique."""
        logger.info(f"Recherche: {query} (limit: {limit})")
        
        try:
            # Génération de l'embedding de la requête
            query_embedding = self.model.encode(query)
            
            # Récupération des documents
            documents = self.db_session.query(Document).all()
            similarities = []
            
            # Calcul des similarités
            for doc in documents:
                if doc.embedding:  # Vérification que l'embedding existe
                    doc_embedding = np.array(doc.get_embedding())
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    similarities.append((doc, similarity))
            
            # Tri et limite des résultats
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:limit]
            
            # Formatage des résultats
            results = []
            for doc, sim in top_results:
                preview = doc.content[:200] + '...' if len(doc.content) > 200 else doc.content
                results.append({
                    'id': doc.id,
                    'title': doc.title,
                    'preview': preview,
                    'similarity': float(sim)
                })
            
            logger.info(f"Recherche complétée: {len(results)} résultats")
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche: {str(e)}")
            raise
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcule la similarité cosinus entre deux vecteurs."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
