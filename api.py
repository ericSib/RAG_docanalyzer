from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import json
import os
from pathlib import Path

# Import du module d'analyse existant
from analyze import BatchDocumentAnalyzer

app = FastAPI(title="RAG Document Analyzer API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage en mémoire pour les jobs (à remplacer par une BD en production)
analysis_jobs = {}

# Initialisation de l'analyseur
analyzer = BatchDocumentAnalyzer()

class AnalysisConfig(BaseModel):
    mode: str = "standard"  # standard, approfondi, rapide
    quality: str = "moyenne"  # haute, moyenne, basse
    language: str = "auto"
    chunk_size: int = 500
    overlap: int = 50

class AnalysisStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, error
    progress: Dict[str, float]  # progression par étape
    current_file: Optional[str] = None
    stats: Dict[str, Any] = {}
    error: Optional[str] = None

# Création des dossiers nécessaires
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload/", response_model=Dict[str, str])
async def upload_files(
    files: List[UploadFile] = File(...),
    mode: str = "standard",
    background_tasks: BackgroundTasks = None
):
    """Point d'entrée pour l'upload et l'analyse des documents"""
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")
    
    # Génération d'un ID unique pour le job
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    # Sauvegarde des fichiers
    saved_files = []
    try:
        for file in files:
            file_path = job_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            saved_files.append(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")
    
    # Initialisation du statut du job
    analysis_jobs[job_id] = {
        "status": "pending",
        "progress": {
            "preprocessing": 0,
            "embedding": 0,
            "indexing": 0,
            "validation": 0
        },
        "files": saved_files,
        "mode": mode,
        "start_time": datetime.now().isoformat(),
        "stats": {
            "total_files": len(saved_files),
            "processed_files": 0,
            "errors": 0
        }
    }
    
    # Démarrage de l'analyse en arrière-plan
    background_tasks.add_task(process_documents, job_id)
    
    return {"task_id": job_id}

@app.get("/status/{job_id}", response_model=AnalysisStatus)
async def get_status(job_id: str):
    """Récupère le statut d'une analyse en cours"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    
    job = analysis_jobs[job_id]
    return AnalysisStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        current_file=job.get("current_file"),
        stats=job["stats"],
        error=job.get("error")
    )

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    """Récupère les résultats d'une analyse terminée"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    
    job = analysis_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail="L'analyse n'est pas encore terminée"
        )
    
    # Lecture des résultats
    results_file = UPLOAD_DIR / job_id / "results.json"
    if not results_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Résultats non trouvés"
        )
    
    with open(results_file) as f:
        results = json.load(f)
    
    # Calcul du temps de traitement
    start_time = datetime.fromisoformat(job["start_time"])
    end_time = datetime.fromisoformat(job["end_time"])
    processing_time = end_time - start_time
    
    # Format des résultats pour le frontend
    formatted_results = {
        "documents": results["documents"],
        "processing_time": str(processing_time),
        "quality": results.get("quality", "95%")
    }
    
    return formatted_results

async def process_documents(job_id: str):
    """Traitement asynchrone des documents avec suivi de progression"""
    job = analysis_jobs[job_id]
    job["status"] = "processing"
    
    try:
        # Preprocessing
        for progress in range(0, 100, 10):
            job["progress"]["preprocessing"] = progress
            await asyncio.sleep(0.5)  # Simuler le traitement
        job["progress"]["preprocessing"] = 100
        
        # Embedding
        for progress in range(0, 100, 10):
            job["progress"]["embedding"] = progress
            await asyncio.sleep(0.5)  # Simuler le traitement
        job["progress"]["embedding"] = 100
        
        # Indexing
        for progress in range(0, 100, 10):
            job["progress"]["indexing"] = progress
            await asyncio.sleep(0.5)  # Simuler le traitement
        job["progress"]["indexing"] = 100
        
        # Validation
        for progress in range(0, 100, 10):
            job["progress"]["validation"] = progress
            await asyncio.sleep(0.5)  # Simuler le traitement
        job["progress"]["validation"] = 100
        
        # Traitement réel des documents
        output_dir = UPLOAD_DIR / job_id / "output"
        output_dir.mkdir(exist_ok=True)
        
        results = analyzer.process_directory(
            input_path=UPLOAD_DIR / job_id,
            output_dir=output_dir
        )
        
        # Sauvegarde des résultats
        with open(UPLOAD_DIR / job_id / "results.json", "w") as f:
            json.dump(results, f)
        
        # Mise à jour du statut
        job["status"] = "completed"
        job["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        print(f"Erreur lors du traitement du job {job_id}: {str(e)}")

@app.on_event("shutdown")
async def cleanup():
    """Nettoyage des fichiers temporaires à l'arrêt"""
    import shutil
    try:
        shutil.rmtree(UPLOAD_DIR)
    except Exception as e:
        print(f"Erreur lors du nettoyage: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
