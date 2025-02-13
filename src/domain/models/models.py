"""Module de gestion des modèles locaux."""
import os
from pathlib import Path
import json
import shutil
import spacy
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from .config import config

class ModelManager:
    def __init__(self):
        self.models_dir = config.models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.models_dir / 'models_config.json'
        self.load_config()

    def load_config(self):
        """Charge la configuration des modèles."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'spacy_model': {
                    'name': config.spacy_model,
                    'downloaded': False,
                    'path': None
                },
                'embedding_model': {
                    'name': config.embedding_model,
                    'downloaded': False,
                    'path': None
                }
            }
            self.save_config()

    def save_config(self):
        """Sauvegarde la configuration des modèles."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    def ensure_spacy_model(self):
        """S'assure que le modèle spaCy est disponible."""
        if not self.config['spacy_model']['downloaded']:
            print(f"Téléchargement du modèle spaCy {config.spacy_model}...")
            spacy.cli.download(config.spacy_model)
            model = spacy.load(config.spacy_model)
            model_path = self.models_dir / 'spacy'
            if model_path.exists():
                shutil.rmtree(model_path)
            shutil.copytree(Path(model.path), model_path)
            self.config['spacy_model']['downloaded'] = True
            self.config['spacy_model']['path'] = str(model_path)
            self.save_config()
        return self.config['spacy_model']['path']

    def ensure_embedding_model(self):
        """S'assure que le modèle d'embedding est disponible."""
        if not self.config['embedding_model']['downloaded']:
            print(f"Téléchargement du modèle d'embedding {config.embedding_model}...")
            model = SentenceTransformer(config.embedding_model)
            model_path = self.models_dir / 'embeddings'
            if model_path.exists():
                shutil.rmtree(model_path)
            shutil.copytree(Path(model.get_model_path()), model_path)
            self.config['embedding_model']['downloaded'] = True
            self.config['embedding_model']['path'] = str(model_path)
            self.save_config()
        return self.config['embedding_model']['path']

    def get_spacy_model(self):
        """Récupère le modèle spaCy."""
        model_path = self.ensure_spacy_model()
        return spacy.load(model_path)

    def get_embedding_model(self):
        """Récupère le modèle d'embedding."""
        model_path = self.ensure_embedding_model()
        return SentenceTransformer(model_path)

# Instance unique du gestionnaire de modèles
model_manager = ModelManager()
