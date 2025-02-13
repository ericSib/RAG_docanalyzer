from pathlib import Path
from datetime import datetime
import concurrent.futures
import multiprocessing
import json
from typing import Union, Dict, Any, List, Tuple
from tqdm import tqdm
import logging
import spacy
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from contextlib import nullcontext
import os
from PyPDF2 import PdfReader

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_text_from_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text and metadata from a file
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    metadata = {
        "filename": path.name,
        "file_size": path.stat().st_size,
        "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
    }
    
    try:
        if path.suffix.lower() == '.pdf':
            reader = PdfReader(path)
            metadata["num_pages"] = len(reader.pages)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        else:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        metadata["char_count"] = len(text)
        return text, metadata
        
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        raise

def create_chunks(text: str, nlp, max_tokens: int = 500, overlap: float = 0.1) -> List[Dict[str, Any]]:
    """
    Creates semantic chunks from text using spaCy with proper sentence boundaries
    """
    # Add sentencizer if not present
    if 'sentencizer' not in nlp.pipe_names:
        nlp.add_pipe('sentencizer')
    
    doc = nlp(text)
    sentences = list(doc.sents)
    chunks = []
    
    current_chunk = []
    current_length = 0
    overlap_tokens = int(max_tokens * overlap)
    
    for sent in sentences:
        sent_tokens = len(sent)
        
        if current_length + sent_tokens > max_tokens and current_chunk:
            # Create chunk
            chunk_text = " ".join(str(s) for s in current_chunk)
            chunks.append({
                "text": chunk_text,
                "start_idx": current_chunk[0].start_char,
                "length": len(chunk_text)
            })
            
            # Keep last sentences for overlap
            overlap_size = 0
            overlap_chunk = []
            for s in reversed(current_chunk):
                if overlap_size + len(s) <= overlap_tokens:
                    overlap_chunk.insert(0, s)
                    overlap_size += len(s)
                else:
                    break
            
            current_chunk = overlap_chunk
            current_length = overlap_size
        
        current_chunk.append(sent)
        current_length += sent_tokens
    
    # Add last chunk if it exists
    if current_chunk:
        chunk_text = " ".join(str(s) for s in current_chunk)
        chunks.append({
            "text": chunk_text,
            "start_idx": current_chunk[0].start_char,
            "length": len(chunk_text)
        })
    
    return chunks

class BatchDocumentAnalyzer:
    def __init__(self, batch_size: int = 32, max_workers: int = None):
        """
        Optimized document analyzer for batch processing
        
        Args:
            batch_size: Batch size for embeddings
            max_workers: Maximum number of workers for parallelism
        """
        self.nlp = spacy.load('fr_core_news_sm')
        # Add sentencizer for proper sentence segmentation
        if 'sentencizer' not in self.nlp.pipe_names:
            self.nlp.add_pipe('sentencizer')
            
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.batch_size = batch_size
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.supported_extensions = {'.pdf'}  # Extensible for other formats
        
        # CUDA optimization if available
        if torch.cuda.is_available():
            self.embedding_model = self.embedding_model.to('cuda')
            logger.info("Using CUDA for embeddings")
        else:
            logger.info("Using CPU for embeddings")
            
    def scan_directory(self, input_path: Union[str, Path]) -> List[Path]:
        """
        Recursively scan a directory for supported documents
        """
        input_path = Path(input_path)
        files = []
        
        if input_path.is_file():
            if input_path.suffix.lower() in self.supported_extensions:
                files.append(input_path)
        else:
            for ext in self.supported_extensions:
                files.extend(input_path.rglob(f"*{ext}"))
        
        return sorted(files)  # Sort for deterministic processing
        
    def process_directory(self, input_path: Union[str, Path], output_dir: str,
                         max_files: int = None) -> Dict[str, Any]:
        """
        Process all documents in a directory
        
        Args:
            input_path: Path to directory or file to process
            output_dir: Output directory
            max_files: Optional limit on number of files to process
        """
        # Scan files
        files = self.scan_directory(input_path)
        logger.info(f"Found {len(files)} documents to process")
        
        if max_files:
            files = files[:max_files]
            logger.info(f"Limited to {max_files} files")
            
        # Create output structure
        output_dir = Path(output_dir)
        batch_dir = output_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize report
        batch_report = {
            "start_time": datetime.now().isoformat(),
            "input_path": str(input_path),
            "total_files": len(files),
            "processed_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "files": {}
        }
        
        # Real-time report update
        report_path = batch_dir / "batch_report.json"
        def update_report():
            with report_path.open('w', encoding='utf-8') as f:
                json.dump(batch_report, f, ensure_ascii=False, indent=2)
        
        # Process files
        with tqdm(total=len(files), desc="Processing documents") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {
                    executor.submit(self._process_single_document, str(file)): file 
                    for file in files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        result = future.result()
                        
                        # Save individual results
                        doc_dir = batch_dir / file.stem
                        self._save_document_results(result, doc_dir)
                        
                        # Update report
                        batch_report["files"][str(file)] = {
                            "status": "success",
                            "chunks": len(result["chunks"]),
                            "file_size": file.stat().st_size,
                            "processing_time": result.get("processing_time", 0)
                        }
                        batch_report["successful_files"] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing {file}: {str(e)}")
                        batch_report["files"][str(file)] = {
                            "status": "error",
                            "error": str(e),
                            "file_size": file.stat().st_size
                        }
                        batch_report["failed_files"] += 1
                    
                    batch_report["processed_files"] += 1
                    update_report()
                    pbar.update(1)
        
        # Finalize report
        batch_report["end_time"] = datetime.now().isoformat()
        batch_report["total_time"] = (
            datetime.fromisoformat(batch_report["end_time"]) - 
            datetime.fromisoformat(batch_report["start_time"])
        ).total_seconds()
        update_report()
        
        return batch_report

    def _process_single_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single document with optimizations
        """
        start_time = datetime.now()
        try:
            logger.info(f"Processing {file_path}")
            
            # Extract text and metadata
            text, metadata = extract_text_from_file(file_path)
            
            # Create chunks using the initialized spaCy model with sentencizer
            chunks = create_chunks(text, self.nlp)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Generate embeddings
            chunks_with_embeddings = self._generate_embeddings(chunks)
            
            result = {
                "metadata": metadata,
                "chunks": chunks_with_embeddings,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
            
            logger.info(f"Processing completed for {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    def _generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for chunks in batches
        """
        texts = [chunk["text"] for chunk in chunks]
        with tqdm(total=1, desc="Generating embeddings", leave=True) as pbar:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            pbar.update(1)
        
        # Convert numpy arrays to lists for JSON serialization
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding.tolist()
        
        return chunks

    def _save_document_results(self, results: Dict[str, Any], output_path: Path):
        """
        Save results for a document
        """
        output_path.mkdir(exist_ok=True)
        
        # Save JSON main file with embeddings
        with open(output_path / 'analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Also save embeddings separately as numpy array for efficient loading
        embeddings = np.array([chunk["embedding"] for chunk in results["chunks"]])
        np.save(output_path / 'embeddings.npy', embeddings)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Optimized document analysis')
    parser.add_argument('input', help='Path to directory or file to analyze')
    parser.add_argument('--output_dir', default='output', help='Output directory')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size for embeddings')
    parser.add_argument('--workers', type=int, default=None, help='Number of workers')
    parser.add_argument('--max_files', type=int, help='Maximum number of files to process')
    args = parser.parse_args()
    
    analyzer = BatchDocumentAnalyzer(batch_size=args.batch_size, max_workers=args.workers)
    results = analyzer.process_directory(args.input, args.output_dir, max_files=args.max_files)
    
    print(f"\nProcessing completed:")
    print(f"- Documents processed: {results['processed_files']}")
    print(f"- Successful: {results['successful_files']}")
    print(f"- Failed: {results['failed_files']}")
    print(f"- Total time: {results['total_time']:.1f} seconds")
