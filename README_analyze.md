# RAG Document Analyzer - Version Locale

Ce script fournit une version simplifiée du RAG Document Analyzer pour un usage local. Il permet d'analyser des documents, de générer des chunks et des embeddings, et de sauvegarder les résultats localement.

## Prérequis

```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_md
```

## Utilisation

```bash
python analyze.py <chemin_du_document> [--output-dir <dossier_sortie>]
```

Exemple :
```bash
python analyze.py documents/exemple.pdf --output-dir output
```

## Structure des résultats

Pour chaque document analysé, un dossier avec un timestamp est créé contenant :

- `metadata.json` : Métadonnées et métriques du document
- `chunks.txt` : Chunks de texte générés
- `embeddings.npy` : Embeddings au format NumPy

## Limitations

- Optimisé pour des documents < 10Mo
- Support des formats texte et PDF
- Modèle multilingue (fr/en) mais optimisé pour le français

## Métriques

Le script calcule et sauvegarde les métriques suivantes :
- Nombre de mots
- Nombre de pages
- Nombre de chunks
- Taille des chunks (tokens)
- Temps de traitement

## Logs

Les logs sont disponibles dans :
- Console (temps réel)
- `analyze.log` (historique complet)

## Document Analyzer

This module provides a powerful and optimized document analyzer that processes text documents in batches, generates embeddings, and saves analysis results.

## Features

- Parallel document processing with configurable number of workers
- CUDA optimization for embedding generation when available
- Batch processing of embeddings for better performance
- Automatic chunking of documents into semantic units
- Incremental saving of results
- Comprehensive batch report generation

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Download the required spaCy model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Command Line Interface

```bash
python analyze.py input_files [--output_dir OUTPUT_DIR] [--batch_size BATCH_SIZE] [--workers WORKERS]
```

Arguments:
- `input_files`: One or more paths to documents to analyze
- `--output_dir`: Output directory for results (default: 'output')
- `--batch_size`: Batch size for embedding generation (default: 32)
- `--workers`: Number of parallel workers (default: CPU count)

### Python API

```python
from analyze import BatchDocumentAnalyzer

# Initialize analyzer
analyzer = BatchDocumentAnalyzer(batch_size=32)

# Process single document
results = analyzer.process_documents("path/to/document.txt", "output_dir")

# Process multiple documents
results = analyzer.process_documents(["doc1.txt", "doc2.txt"], "output_dir")
```

## Output Structure

For each processed document, the analyzer creates:
1. `analysis_results.json`: Contains metadata and text chunks
2. `embeddings.npy`: NumPy array of embeddings for efficient storage

A batch report (`batch_report.json`) is also generated with processing statistics.
