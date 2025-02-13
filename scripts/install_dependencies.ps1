# Configuration de conda
$condaPath = "$env:USERPROFILE\miniconda3"
$condaExe = "$condaPath\Scripts\conda.exe"

if (-not (Test-Path $condaExe)) {
    Write-Host "Erreur : Miniconda n'est pas installé dans le répertoire par défaut." -ForegroundColor Red
    Write-Host "Veuillez d'abord installer Miniconda : https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Red
    exit 1
}

# Initialisation de conda
& "$condaPath\shell\condabin\conda-hook.ps1"

# Installation des packages conda
Write-Host "Installation de PyTorch avec CUDA..." -ForegroundColor Yellow
& $condaExe install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y

Write-Host "`nInstallation de sentence-transformers..." -ForegroundColor Yellow
& $condaExe install -c conda-forge sentence-transformers -y

# Installation des packages pip
Write-Host "`nInstallation des autres dépendances via pip..." -ForegroundColor Yellow
pip install spacy sqlalchemy psycopg2-binary tqdm

# Installation du modèle français spaCy
Write-Host "`nInstallation du modèle français spaCy..." -ForegroundColor Yellow
python -m spacy download fr_core_news_md

Write-Host "`nToutes les dépendances ont été installées avec succès !" -ForegroundColor Green

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
