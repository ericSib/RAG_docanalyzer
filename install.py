import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Installe les dépendances du projet."""
    print("Installation des dependances...")
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            "requirements.txt"
        ], check=True)
        print("[OK] Dependances installees")
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Erreur lors de l'installation des dependances: {e}")
        sys.exit(1)

def install_spacy_model():
    """Télécharge et installe le modèle français de spaCy."""
    print("Installation du modele spaCy...")
    try:
        # Installation directe via pip pour éviter les problèmes de permission
        subprocess.run([
            sys.executable,
            "-m",
            "pip",
            "install",
            "https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.7.0/fr_core_news_md-3.7.0-py3-none-any.whl"
        ], check=True)
        print("[OK] Modele spaCy installe")
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Erreur lors de l'installation du modele spaCy: {e}")
        sys.exit(1)

def create_data_directories():
    """Crée les répertoires nécessaires."""
    print("Creation des repertoires...")
    try:
        Path("data").mkdir(exist_ok=True)
        print("[OK] Repertoires crees")
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la creation des repertoires: {e}")
        sys.exit(1)

def verify_installation():
    """Vérifie l'installation."""
    print("\nVerification de l'installation...")
    try:
        # Vérification de spaCy
        import spacy
        nlp = spacy.load("fr_core_news_md")
        print("[OK] spaCy et modele francais verifies")
        
        # Vérification de sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("[OK] Sentence Transformers verifie")
        
        print("\n[OK] Installation complete et verifiee!")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la verification: {e}")
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
        print("\n[OK] Configuration terminee avec succes!")
    else:
        print("\n[ERREUR] Des erreurs sont survenues lors de la configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()
