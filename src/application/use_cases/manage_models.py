"""Model management use case module."""
from typing import Dict, Optional
from ...domain.interfaces.services import ModelService
from pathlib import Path

class ManageModelsUseCase:
    """Cas d'utilisation pour la gestion des modèles."""

    def __init__(self, model_service: ModelService):
        self.model_service = model_service

    async def ensure_models_ready(self) -> bool:
        """S'assure que tous les modèles sont disponibles."""
        return await self.model_service.ensure_models_available()

    async def get_model_status(self) -> Dict[str, Dict]:
        """Récupère le statut des modèles."""
        models = {
            'spacy': 'fr_core_news_md',
            'embeddings': 'paraphrase-multilingual-MiniLM-L12-v2'
        }
        
        status = {}
        for name, model in models.items():
            status[name] = await self.model_service.get_model_info(model)
        
        return status

    async def download_model(self, model_name: str) -> bool:
        """Télécharge un modèle spécifique."""
        try:
            return await self.model_service.download_model(model_name)
        except Exception:
            return False
