from pathlib import Path
import shutil

# Stockage en mémoire pour les jobs
analysis_jobs = {}

# Création du dossier temporaire pour les uploads
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def cleanup_temp_files():
    """Nettoyage des fichiers temporaires"""
    try:
        shutil.rmtree(UPLOAD_DIR)
    except Exception as e:
        print(f"Erreur lors du nettoyage: {str(e)}")
