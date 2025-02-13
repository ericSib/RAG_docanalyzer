from datetime import datetime
import json
from .analyze import BatchDocumentAnalyzer
from .config import UPLOAD_DIR

# Stockage en mémoire pour les jobs
analysis_jobs = {}

# Initialisation de l'analyseur
analyzer = BatchDocumentAnalyzer()

async def process_documents(job_id: str):
    """Traitement asynchrone des documents"""
    job = analysis_jobs[job_id]
    job["status"] = "processing"
    
    try:
        config = job["config"]
        mode = config["mode"]
        
        output_dir = UPLOAD_DIR / job_id / "output"
        results = analyzer.process_directory(
            input_path=UPLOAD_DIR / job_id,
            output_dir=output_dir
        )
        
        with open(UPLOAD_DIR / job_id / "results.json", "w") as f:
            json.dump(results, f)
        
        job["status"] = "completed"
        job["progress"] = 100
        job["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        print(f"Erreur lors du traitement du job {job_id}: {str(e)}")
