from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from typing import List
from datetime import datetime
import json

from .models import AnalysisConfig, AnalysisStatus
from .services import process_documents, analysis_jobs
from .config import UPLOAD_DIR

router = APIRouter()

@router.post("/analyze/", response_model=AnalysisStatus)
async def start_analysis(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    config: str = Form(None)  # Configuration reçue en tant que string JSON
):
    """
    Démarre une nouvelle analyse de documents.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")
    
    # Parse la config si fournie
    analysis_config = None
    if config:
        try:
            config_dict = json.loads(config)
            analysis_config = AnalysisConfig(**config_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Configuration invalide: {str(e)}")

    # Création du job
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
            saved_files.append(str(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")
    
    # Initialisation du job
    analysis_jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "files": saved_files,
        "config": analysis_config.dict() if analysis_config else {"mode": "standard"},
        "start_time": datetime.now().isoformat(),
        "stats": {
            "total_files": len(saved_files),
            "processed_files": 0,
            "errors": 0
        }
    }
    
    # Démarrage du traitement en arrière-plan
    background_tasks.add_task(process_documents, job_id)
    
    return AnalysisStatus(
        job_id=job_id,
        status="pending",
        progress=0,
        stats=analysis_jobs[job_id]["stats"]
    )

@router.get("/analysis/{job_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(job_id: str):
    """
    Récupère le statut d'une analyse en cours.
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} non trouvé")
    
    job = analysis_jobs[job_id]
    return AnalysisStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        current_file=job.get("current_file"),
        stats=job["stats"],
        error=job.get("error")
    )

@router.get("/analysis/{job_id}/results")
async def get_analysis_results(job_id: str):
    """
    Récupère les résultats d'une analyse terminée.
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} non trouvé")
    
    job = analysis_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail="L'analyse n'est pas encore terminée"
        )
    
    results_file = UPLOAD_DIR / job_id / "results.json"
    if not results_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Résultats non trouvés"
        )
    
    with open(results_file) as f:
        results = json.load(f)
    
    return results
