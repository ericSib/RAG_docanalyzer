from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os
from app.core.config import settings
from app.core.analyzer import DocumentAnalyzer
from loguru import logger

app = FastAPI(title=settings.APP_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = DocumentAnalyzer()

# Ensure upload directory exists
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)

@app.post("/api/v1/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze an uploaded document and return the analysis results.
    """
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {settings.SUPPORTED_EXTENSIONS}"
            )
        
        # Save uploaded file
        file_path = upload_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Analyze document
        results = analyzer.analyze_document(file_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/api/v1/health")
async def health_check():
    """
    Check the health status of the API.
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }
