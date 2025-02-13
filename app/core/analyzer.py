from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import spacy
from sentence_transformers import SentenceTransformer
from app.core.config import analyzer_config, settings
from app.models.document import Document, DocumentChunk
from app.core.cache import AnalysisCache
from app.core.temp_manager import TempFileManager
from loguru import logger
import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation
import textstat
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
from datetime import datetime

class DocumentAnalyzer:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the document analyzer with custom or default configuration.
        
        Args:
            config: Optional custom configuration to override defaults
        """
        self.config = config or analyzer_config
        try:
            self.nlp = spacy.load(self.config['SPACY_MODEL'])
            self.embedding_model = SentenceTransformer(self.config['EMBEDDING_MODEL'])
            self.cache = AnalysisCache()
            self.temp_manager = TempFileManager()
            self.executor = ThreadPoolExecutor(max_workers=self.config.get('MAX_PARALLEL_PROCESSES', 4))
            
            logger.info(f"Initialized analyzer with spaCy model: {self.config['SPACY_MODEL']}")
            logger.info(f"Using embedding model: {self.config['EMBEDDING_MODEL']}")
        except Exception as e:
            logger.error(f"Error initializing analyzer: {str(e)}")
            raise
    
    async def analyze_document(
        self,
        file_path: Union[str, Path],
        doc_id: str,
        force_reanalysis: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a document asynchronously and return comprehensive analysis results.
        
        Args:
            file_path: Path to the document file
            doc_id: Unique identifier for the document
            force_reanalysis: If True, bypass cache and reanalyze
            
        Returns:
            Dictionary containing analysis results
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
            
        try:
            # Check cache first
            if not force_reanalysis:
                cached_result = self.cache.retrieve(doc_id, "analysis")
                if cached_result:
                    logger.info(f"Retrieved cached analysis for document {doc_id}")
                    return cached_result
            
            # Generate document hash for tracking
            doc_hash = await self._compute_document_hash(file_path)
            
            # Extract content and metadata
            metadata = await self._extract_metadata(file_path)
            content = await self._extract_content(file_path)
            
            # Analyze content in parallel
            analysis_tasks = [
                self._analyze_content(content),
                self._generate_chunks(content),
                self._compute_document_metrics(content)
            ]
            
            content_analysis, chunks, metrics = await asyncio.gather(*analysis_tasks)
            
            # Process chunks in parallel
            processed_chunks = await self._process_chunks(chunks)
            
            # Compile results
            result = {
                "document_id": doc_id,
                "document_hash": doc_hash,
                "metadata": metadata,
                "analysis": content_analysis,
                "metrics": metrics,
                "chunks": processed_chunks,
                "processed_at": datetime.now().isoformat()
            }
            
            # Cache the results
            self.cache.store(doc_id, result, "analysis", {
                "document_hash": doc_hash,
                "file_path": str(file_path)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing document {doc_id}: {str(e)}")
            raise
    
    async def _compute_document_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of document content."""
        def _compute():
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
            
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _compute
        )
    
    async def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from document asynchronously."""
        def _extract():
            file_type = file_path.suffix.lower()
            metadata = {
                "filename": file_path.name,
                "file_type": file_type,
                "file_size": file_path.stat().st_size
            }
            
            try:
                if file_type == ".pdf":
                    with open(file_path, "rb") as f:
                        pdf = PyPDF2.PdfReader(f)
                        metadata.update({
                            "page_count": len(pdf.pages),
                            "title": pdf.metadata.get("/Title", ""),
                            "author": pdf.metadata.get("/Author", ""),
                            "creation_date": pdf.metadata.get("/CreationDate", "")
                        })
                
                elif file_type == ".docx":
                    doc = DocxDocument(file_path)
                    metadata.update({
                        "page_count": len(doc.sections),
                        "word_count": len(doc.paragraphs)
                    })
                    
                elif file_type == ".pptx":
                    prs = Presentation(file_path)
                    metadata.update({
                        "slide_count": len(prs.slides)
                    })
                    
            except Exception as e:
                logger.warning(f"Error extracting metadata: {str(e)}")
                
            return metadata
            
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _extract
        )
    
    async def _extract_content(self, file_path: Path) -> str:
        """Extract text content from document asynchronously."""
        def _extract():
            file_type = file_path.suffix.lower()
            content = ""
            
            try:
                if file_type == ".pdf":
                    with open(file_path, "rb") as f:
                        pdf = PyPDF2.PdfReader(f)
                        content = "\n".join(page.extract_text() for page in pdf.pages)
                        
                elif file_type == ".docx":
                    doc = DocxDocument(file_path)
                    content = "\n".join(paragraph.text for paragraph in doc.paragraphs)
                    
                elif file_type == ".pptx":
                    prs = Presentation(file_path)
                    content = "\n".join(
                        shape.text
                        for slide in prs.slides
                        for shape in slide.shapes
                        if hasattr(shape, "text")
                    )
                    
                elif file_type == ".txt":
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
            except Exception as e:
                logger.error(f"Error extracting content: {str(e)}")
                raise
                
            return content
            
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _extract
        )
    
    async def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze the content asynchronously."""
        def _analyze():
            doc = self.nlp(content)
            
            # Calculate basic metrics
            word_count = len(doc)
            sentence_count = len(list(doc.sents))
            
            # Calculate complexity metrics
            complexity_score = textstat.flesch_reading_ease(content)
            
            # Calculate information density
            unique_words = len(set(token.text.lower() for token in doc if not token.is_stop))
            information_density = unique_words / word_count if word_count > 0 else 0
            
            # Extract key entities
            entities = [
                {"text": ent.text, "label": ent.label_}
                for ent in doc.ents
            ]
            
            return {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "complexity_score": complexity_score,
                "information_density": information_density,
                "entities": entities
            }
            
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _analyze
        )
    
    async def _generate_chunks(self, content: str) -> List[str]:
        """Generate overlapping chunks asynchronously."""
        def _chunk():
            doc = self.nlp(content)
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sent in doc.sents:
                sent_length = len(sent.text.split())
                
                if current_length + sent_length > self.config['CHUNK_SIZE']:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                    # Add overlap from previous chunk
                    if chunks and self.config['OVERLAP_SIZE'] > 0:
                        words = chunks[-1].split()[-self.config['OVERLAP_SIZE']:]
                        current_chunk = [" ".join(words), sent.text]
                        current_length = len(words) + sent_length
                    else:
                        current_chunk = [sent.text]
                        current_length = sent_length
                else:
                    current_chunk.append(sent.text)
                    current_length += sent_length
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                
            return chunks
            
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _chunk
        )
    
    async def _process_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Process chunks in parallel."""
        async def _process_chunk(chunk: str, index: int) -> Dict[str, Any]:
            # Generate embedding
            embedding = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.embedding_model.encode(chunk)
            )
            
            # Calculate chunk quality
            quality_score = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self._calculate_chunk_quality(chunk)
            )
            
            return {
                "content": chunk,
                "chunk_index": index,
                "embedding": embedding.tolist(),
                "quality_score": quality_score
            }
        
        tasks = [_process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        return await asyncio.gather(*tasks)
    
    async def _compute_document_metrics(self, content: str) -> Dict[str, Any]:
        """Compute document-level metrics asynchronously."""
        def _compute():
            return {
                "total_length": len(content),
                "readability_score": textstat.flesch_reading_ease(content),
                "automated_readability_index": textstat.automated_readability_index(content),
                "coleman_liau_index": textstat.coleman_liau_index(content)
            }
            
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _compute
        )
    
    def _calculate_chunk_quality(self, chunk: str) -> float:
        """Calculate the quality score for a chunk."""
        try:
            # Basic quality checks
            if not chunk.strip():
                return 0.0
                
            # Check for coherent sentences
            doc = self.nlp(chunk)
            sentences = list(doc.sents)
            if not sentences:
                return 0.2
                
            # Calculate quality metrics
            words = chunk.split()
            unique_words = len(set(words))
            total_words = len(words)
            
            if total_words < self.config['MIN_CHUNK_LENGTH']:
                return 0.0
                
            if total_words == 0:
                return 0.0
                
            # Vocabulary richness
            vocabulary_richness = unique_words / total_words
            
            # Sentence structure quality
            has_verbs = any(token.pos_ == "VERB" for token in doc)
            has_nouns = any(token.pos_ == "NOUN" for token in doc)
            
            # Combine metrics
            quality_score = (
                vocabulary_richness * 0.4 +
                (1.0 if has_verbs else 0.0) * 0.3 +
                (1.0 if has_nouns else 0.0) * 0.3
            )
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating chunk quality: {str(e)}")
            return 0.0
    
    async def close(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        # Additional cleanup if needed
