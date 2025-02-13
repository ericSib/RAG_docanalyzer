from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Any
import spacy
from sentence_transformers import SentenceTransformer
from .anomaly_detection import AnomalyDetector
from .cache import Cache
from .temp_manager import TempManager
from ..models.document import Document, DocumentChunk, AnalysisResult

class DocumentAnalyzer:
    """Analyseur central pour le traitement des documents."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'analyseur avec la configuration fournie.
        
        Args:
            config: Dictionnaire de configuration contenant:
                - chunk_size: Taille des segments de texte
                - overlap_size: Taille du chevauchement entre segments
                - embedding_model: Nom du modèle de transformer à utiliser
                - spacy_model: Nom du modèle spaCy à utiliser
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des composants
        self.nlp = spacy.load(config['spacy_model'])
        self.embedding_model = SentenceTransformer(config['embedding_model'])
        self.anomaly_detector = AnomalyDetector()
        self.cache = Cache()
        self.temp_manager = TempManager()
        
    async def analyze_document(self, 
                             file_path: Path,
                             document_id: str) -> AnalysisResult:
        """
        Analyse complète d'un document.
        
        Args:
            file_path: Chemin vers le fichier à analyser
            document_id: Identifiant unique du document
            
        Returns:
            AnalysisResult: Résultats complets de l'analyse
        """
        try:
            # Vérification du cache
            cached_result = await self.cache.get_analysis(document_id)
            if cached_result:
                self.logger.info(f"Résultats trouvés en cache pour {document_id}")
                return cached_result
            
            # Extraction du texte
            text = await self._extract_text(file_path)
            
            # Prétraitement
            cleaned_text = await self._preprocess_text(text)
            
            # Segmentation
            chunks = await self._create_chunks(cleaned_text)
            
            # Analyse des anomalies
            anomalies = await self.anomaly_detector.analyze(chunks)
            
            # Génération des embeddings
            embeddings = await self._generate_embeddings(chunks)
            
            # Analyse sémantique
            semantic_analysis = await self._analyze_semantics(chunks)
            
            # Création du résultat
            result = AnalysisResult(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings,
                anomalies=anomalies,
                semantic_analysis=semantic_analysis,
                metadata=await self._extract_metadata(file_path)
            )
            
            # Mise en cache
            await self.cache.store_analysis(document_id, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse du document {document_id}: {str(e)}")
            raise
            
    async def _extract_text(self, file_path: Path) -> str:
        """Extrait le texte du document selon son format."""
        # Utilisation du gestionnaire temporaire pour les fichiers
        with self.temp_manager.handle_file(file_path) as temp_file:
            # Logique d'extraction selon le type de fichier
            extension = file_path.suffix.lower()
            if extension == '.pdf':
                return await self._extract_from_pdf(temp_file)
            elif extension in ['.docx', '.doc']:
                return await self._extract_from_word(temp_file)
            elif extension in ['.pptx', '.ppt']:
                return await self._extract_from_powerpoint(temp_file)
            else:
                return await self._extract_from_text(temp_file)

    async def _preprocess_text(self, text: str) -> str:
        """Prétraitement du texte extrait."""
        doc = self.nlp(text)
        # Nettoyage et normalisation
        cleaned_text = ' '.join([
            token.text for token in doc 
            if not token.is_space and not token.is_punct
        ])
        return cleaned_text
        
    async def _create_chunks(self, text: str) -> List[DocumentChunk]:
        """Création des segments de texte avec chevauchement."""
        chunks = []
        words = text.split()
        chunk_size = self.config['chunk_size']
        overlap = self.config['overlap_size']
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_text = ' '.join(words[i:i + chunk_size])
            if chunk_text:
                chunk = DocumentChunk(
                    text=chunk_text,
                    start_idx=i,
                    end_idx=min(i + chunk_size, len(words))
                )
                chunks.append(chunk)
                
        return chunks
        
    async def _generate_embeddings(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """Génère les embeddings pour chaque segment."""
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
        
    async def _analyze_semantics(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Analyse sémantique des segments."""
        docs = list(self.nlp.pipe([chunk.text for chunk in chunks]))
        
        return {
            'entities': [self._extract_entities(doc) for doc in docs],
            'key_phrases': [self._extract_key_phrases(doc) for doc in docs],
            'sentiment': [self._analyze_sentiment(doc) for doc in docs]
        }
        
    async def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extraction des métadonnées du document."""
        # À implémenter selon les besoins spécifiques
        pass
        
    def _extract_entities(self, doc) -> List[Dict[str, Any]]:
        """Extraction des entités nommées."""
        return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
        
    def _extract_key_phrases(self, doc) -> List[str]:
        """Extraction des phrases clés."""
        return [chunk.text for chunk in doc.noun_chunks]
        
    def _analyze_sentiment(self, doc) -> float:
        """Analyse du sentiment (à adapter selon les besoins)."""
        # Implémentation basique - à personnaliser
        return sum(token.sentiment for token in doc) / len(doc)
