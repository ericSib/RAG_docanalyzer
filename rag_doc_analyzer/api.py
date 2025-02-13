from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from datetime import datetime

from .document_processor import DocumentProcessor
from .database import get_db, init_db

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Document Analyzer API",
    description="API pour l'analyse et la recherche sémantique de documents",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.on_event("startup")
async def startup():
    """Initialisation de l'application."""
    try:
        init_db()
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise

def validate_file_size(file: UploadFile, max_size_mb: int = 10) -> None:
    """Valide la taille du fichier."""
    max_size_bytes = max_size_mb * 1024 * 1024  # Conversion en bytes
    file_size = 0
    chunk_size = 8192  # 8KB chunks
    
    while True:
        chunk = file.file.read(chunk_size)
        if not chunk:
            break
        file_size += len(chunk)
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Le fichier est trop volumineux. Taille maximale: {max_size_mb}MB"
            )
    
    # Remettre le curseur au début du fichier
    file.file.seek(0)

async def process_document_async(
    db: Session,
    content: str,
    title: str
) -> Dict[str, Any]:
    """Traite un document de manière asynchrone."""
    try:
        processor = DocumentProcessor(db)
        return processor.process_document(content=content, title=title)
    except Exception as e:
        logger.error(f"Erreur lors du traitement du document: {str(e)}")
        raise

@app.post("/documents/analyze", 
    response_model=Dict[str, Any],
    summary="Analyse un document",
    description="Analyse un document, génère les embeddings et stocke les résultats en base de données"
)
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Analyse un document et génère les embeddings."""
    try:
        # Validation du fichier
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")
        
        # Validation de la taille du fichier
        validate_file_size(file)
        
        # Lecture du contenu
        content = await file.read()
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être au format texte UTF-8"
            )
        
        # Traitement asynchrone du document
        background_tasks.add_task(
            process_document_async,
            db=db,
            content=text_content,
            title=file.filename
        )
        
        return {
            "status": "processing",
            "message": "Le document est en cours de traitement",
            "document": {
                "title": file.filename,
                "size": len(content),
                "submitted_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@app.post("/search",
    response_model=Dict[str, Any],
    summary="Recherche sémantique",
    description="Effectue une recherche sémantique dans les documents analysés"
)
async def semantic_search(
    query: str,
    limit: Optional[int] = 5,
    min_similarity: Optional[float] = 0.5,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Effectue une recherche sémantique."""
    try:
        if not query.strip():
            raise HTTPException(
                status_code=400,
                detail="La requête ne peut pas être vide"
            )
        
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=400,
                detail="La limite doit être comprise entre 1 et 100"
            )
        
        processor = DocumentProcessor(db)
        results = processor.semantic_search(query, limit)
        
        # Filtrer les résultats par similarité minimale
        filtered_results = [
            r for r in results 
            if r['similarity'] >= min_similarity
        ]
        
        return {
            "status": "success",
            "query": query,
            "results": filtered_results,
            "total": len(filtered_results),
            "limit": limit,
            "min_similarity": min_similarity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health",
    response_model=Dict[str, Any],
    summary="Vérifie l'état du service",
    description="Retourne l'état de santé du service et ses composants"
)
async def health_check(db: Session = Depends(get_db)):
    """Vérifie l'état du service."""
    try:
        # Vérifier la connexion à la base de données
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "components": {
                "database": "up",
                "api": "up"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors du health check: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "rag_doc_analyzer.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
