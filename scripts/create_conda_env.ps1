# Création de l'environnement conda
Write-Host "Création de l'environnement conda..." -ForegroundColor Yellow

# Création de l'environnement à partir du fichier environment.yml
Write-Host "`n1. Création de l'environnement rag_env..."
conda env create -f environment.yml

# Installation du modèle français spaCy
Write-Host "`n2. Installation du modèle français spaCy..."
conda activate rag_env
python -m spacy download fr_core_news_md

Write-Host "`nEnvironnement conda créé avec succès !" -ForegroundColor Green
Write-Host "Pour l'activer, utilisez : conda activate rag_env"

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
