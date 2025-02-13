"""Script de packaging de l'application."""
import subprocess
import sys
from pathlib import Path

def clean_build():
    """Nettoie les fichiers de build."""
    print("Nettoyage des fichiers de build...")
    try:
        for directory in ["build", "dist", "*.egg-info"]:
            subprocess.run(["rm", "-rf", directory], check=True)
        print("✓ Nettoyage effectué")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        sys.exit(1)

def build_package():
    """Crée le package de l'application."""
    print("Construction du package...")
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "PyInstaller",
            "--name=rag-analyzer",
            "--windowed",
            "--onefile",
            "src/ui/windows/main_window.py"
        ], check=True)
        print("✓ Package créé")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création du package: {e}")
        sys.exit(1)

def copy_resources():
    """Copie les ressources nécessaires."""
    print("Copie des ressources...")
    try:
        dist_dir = Path("dist")
        resources_dir = dist_dir / "resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Copie la configuration par défaut
        (resources_dir / "config").mkdir(exist_ok=True)
        subprocess.run([
            "cp",
            "config/default_config.json",
            str(resources_dir / "config")
        ], check=True)
        
        print("✓ Ressources copiées")
    except Exception as e:
        print(f"❌ Erreur lors de la copie des ressources: {e}")
        sys.exit(1)

def main():
    """Point d'entrée du script."""
    print("=== Packaging de RAG Analyzer ===\n")
    
    # Nettoyage
    clean_build()
    
    # Construction
    build_package()
    
    # Ressources
    copy_resources()
    
    print("\n✓ Packaging terminé avec succès!")

if __name__ == "__main__":
    main()
