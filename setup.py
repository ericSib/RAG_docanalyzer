from setuptools import setup, find_packages
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Installe les dépendances du projet."""
    print("Installation des dépendances...")
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            "requirements.txt"
        ], check=True)
        print("✓ Dépendances installées")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances: {e}")
        sys.exit(1)

def install_spacy_model():
    """Télécharge et installe le modèle français de spaCy."""
    print("Installation du modèle spaCy...")
    try:
        # Installation directe via pip pour éviter les problèmes de permission
        subprocess.run([
            sys.executable,
            "-m",
            "pip",
            "install",
            "https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.7.0/fr_core_news_md-3.7.0-py3-none-any.whl"
        ], check=True)
        print("✓ Modèle spaCy installé")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation du modèle spaCy: {e}")
        sys.exit(1)

def create_data_directories():
    """Crée les répertoires nécessaires."""
    print("Création des répertoires...")
    try:
        Path("data").mkdir(exist_ok=True)
        print("✓ Répertoires créés")
    except Exception as e:
        print(f"❌ Erreur lors de la création des répertoires: {e}")
        sys.exit(1)

def verify_installation():
    """Vérifie l'installation."""
    print("\nVérification de l'installation...")
    try:
        # Vérification de spaCy
        import spacy
        nlp = spacy.load("fr_core_news_md")
        print("✓ spaCy et modèle français vérifiés")
        
        # Vérification de sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✓ Sentence Transformers vérifié")
        
        print("\n✓ Installation complète et vérifiée!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    """Fonction principale d'installation."""
    print("=== Configuration de l'environnement RAG ===\n")
    
    # Installation des dépendances
    install_requirements()
    
    # Installation du modèle spaCy
    install_spacy_model()
    
    # Création des répertoires
    create_data_directories()
    
    # Vérification finale
    if verify_installation():
        print("\n✓ Configuration terminée avec succès!")
    else:
        print("\n❌ Des erreurs sont survenues lors de la configuration")
        sys.exit(1)

setup(
    name="rag_doc_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-multipart==0.0.6",
        "sqlalchemy==2.0.23",
        "spacy==3.7.2",
        "sentence-transformers==2.2.2",
        "numpy==1.26.2",
        "python-dotenv==1.0.0",
        "pydantic==2.5.1",
        "loguru==0.7.2",
        "pytest==7.4.3"
    ],
    python_requires=">=3.8",
)

if __name__ == "__main__":
    main()
