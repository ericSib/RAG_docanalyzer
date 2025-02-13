"""
Example script demonstrating how to use the DocumentAnalyzer.
"""
import asyncio
from pathlib import Path
from app.core.analyzer import DocumentAnalyzer
from app.core.config import analyzer_config
import json
from loguru import logger

async def main():
    # Custom configuration (optional)
    custom_config = {
        **analyzer_config,  # Use default config as base
        'CHUNK_SIZE': 512,  # Override with custom values
        'OVERLAP_SIZE': 50,
        'EMBEDDING_MODEL': 'sentence-transformers/all-MiniLM-L6-v2',
        'SPACY_MODEL': 'fr_core_news_lg'
    }
    
    try:
        # Initialize analyzer with custom config
        analyzer = DocumentAnalyzer(custom_config)
        
        # Example document path
        document_path = Path("path/to/your/document.pdf")
        
        # Generate a unique document ID (you might want to use your own ID system)
        doc_id = f"doc_{document_path.stem}"
        
        logger.info(f"Starting analysis of document: {document_path}")
        
        # Analyze document
        result = await analyzer.analyze_document(
            file_path=document_path,
            doc_id=doc_id,
            force_reanalysis=False  # Set to True to bypass cache
        )
        
        # Print analysis results
        print("\nDocument Analysis Results:")
        print("-" * 50)
        
        # Print metadata
        print("\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
            
        # Print content analysis
        print("\nContent Analysis:")
        for key, value in result['analysis'].items():
            if key != 'entities':  # Skip entities for brevity
                print(f"  {key}: {value}")
                
        # Print chunk statistics
        print("\nChunk Statistics:")
        print(f"  Total chunks: {len(result['chunks'])}")
        print(f"  Average chunk quality: {sum(c['quality_score'] for c in result['chunks']) / len(result['chunks']):.2f}")
        
        # Save results to file
        output_file = Path("analysis_results.json")
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"\nFull analysis results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise
        
    finally:
        # Cleanup
        await analyzer.close()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
