"""Script d'installation de l'application."""
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Installe les dépendances Python."""
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
    """Installe le modèle français spaCy."""
    print("Installation du modèle spaCy...")
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "spacy",
            "download",
            "fr_core_news_md"
        ], check=True)
        print("✓ Modèle spaCy installé")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation du modèle spaCy: {e}")
        sys.exit(1)

def create_directories():
    """Crée les répertoires nécessaires."""
    print("Création des répertoires...")
    try:
        for directory in ["data/documents", "data/models"]:
            Path(directory).mkdir(parents=True, exist_ok=True)
            (Path(directory) / ".gitkeep").touch()
        print("✓ Répertoires créés")
    except Exception as e:
        print(f"❌ Erreur lors de la création des répertoires: {e}")
        sys.exit(1)

def main():
    """Point d'entrée du script."""
    print("=== Installation de RAG Analyzer ===\n")
    
    # Installation des dépendances
    install_dependencies()
    
    # Installation du modèle spaCy
    install_spacy_model()
    
    # Création des répertoires
    create_directories()
    
    print("\n✓ Installation terminée avec succès!")

if __name__ == "__main__":
    main()
