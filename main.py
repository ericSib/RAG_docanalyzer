from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import uvicorn
import logging
from typing import Optional, List
import io
from pathlib import Path

from rag_doc_analyzer.database import get_db, init_db, check_db_connection
from rag_doc_analyzer.document_processor import DocumentProcessor
from pydantic import BaseModel, Field, validator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
    ]
)
logger = logging.getLogger(__name__)

# Modèles de données
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Texte à rechercher")
    limit: Optional[int] = Field(default=5, ge=1, le=100)

    @validator('query')
    def query_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("La requête ne peut pas être vide")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "query": "fonctionnement système",
                "limit": 5
            }
        }

class DocumentResponse(BaseModel):
    title: str
    chunks: int
    embeddings: int
    timestamp: str

class SearchResult(BaseModel):
    id: int
    title: str
    preview: str
    similarity: float

class APIResponse(BaseModel):
    status: str
    timestamp: str
    detail: Optional[str] = None
    document: Optional[DocumentResponse] = None
    results: Optional[List[SearchResult]] = None
    count: Optional[int] = None

# Configuration de l'application
app = FastAPI(
    title="RAG Document Analyzer",
    description="API pour l'analyse documentaire avec RAG",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_error_response(message: str, status_code: int = 500) -> JSONResponse:
    """Crée une réponse d'erreur standardisée."""
    return JSONResponse(
        content={
            "status": "error",
            "detail": message,
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=status_code
    )

def create_success_response(data: dict) -> JSONResponse:
    """Crée une réponse de succès standardisée."""
    response = {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }
    response.update(data)
    return JSONResponse(content=response, status_code=200)

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application."""
    if init_db():
        logger.info("Application démarrée avec succès")
    else:
        error_msg = "Erreur lors de l'initialisation de la base de données"
        logger.error(error_msg)
        raise Exception(error_msg)

@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API."""
    db_status = check_db_connection()
    
    return create_success_response({
        "health": "healthy" if db_status else "unhealthy",
        "components": {
            "database": "connected" if db_status else "disconnected",
            "api": "up"
        }
    })

def validate_file(file: UploadFile) -> None:
    """Valide et lit le contenu du fichier."""
    if not file.filename:
        raise ValueError("Nom de fichier manquant")
    
    # Vérification de l'extension
    allowed_extensions = {'.txt', '.md', '.rst'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise ValueError(f"Type de fichier non supporté. Extensions acceptées: {', '.join(allowed_extensions)}")

@app.post("/documents/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyse un document et génère les embeddings."""
    if not file.filename:
        return create_error_response("Nom de fichier manquant", status_code=400)
        
    try:
        # Lecture du contenu avec gestion de la mémoire
        content = await file.read()
        await file.close()
        
        if not content:
            return create_error_response("Fichier vide", status_code=400)
            
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = content.decode('latin-1')
                logger.warning(f"Document {file.filename} décodé en latin-1")
            except UnicodeDecodeError:
                return create_error_response("Encodage non supporté", status_code=400)
        
        if not text_content.strip():
            return create_error_response("Contenu vide après nettoyage", status_code=400)
            
        # Traitement du document
        try:
            processor = DocumentProcessor(db)
            result = processor.process_document(
                content=text_content,
                title=file.filename
            )
            
            return create_success_response({
                "document": {
                    "title": file.filename,
                    "chunks": len(result.get("chunks", [])),
                    "embeddings": len(result.get("embeddings", [])),
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur traitement document: {str(e)}")
            return create_error_response(str(e), status_code=500)
            
    except Exception as e:
        logger.error(f"Erreur lecture fichier: {str(e)}")
        return create_error_response(str(e), status_code=500)

@app.post("/search")
async def semantic_search(query: SearchQuery, db: Session = Depends(get_db)):
    """Effectue une recherche sémantique."""
    try:
        logger.info(f"Recherche: '{query.query}' (limit: {query.limit})")
        
        processor = DocumentProcessor(db)
        results = processor.semantic_search(query.query, query.limit)
        
        response = {
            "results": results,
            "count": len(results)
        }
        
        return create_success_response(response)
        
    except ValueError as e:
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Erreur recherche: {str(e)}")
        return create_error_response(str(e), status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)
