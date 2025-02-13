from pydantic import BaseModel
from typing import Optional, Dict, Any

class AnalysisConfig(BaseModel):
    mode: str = "standard"  # standard, approfondi, rapide
    quality: str = "moyenne"  # haute, moyenne, basse
    language: str = "auto"

class AnalysisStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, error
    progress: float
    current_file: Optional[str] = None
    stats: Dict[str, Any] = {}
    error: Optional[str] = None
