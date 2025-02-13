# Vérifier si l'environnement virtuel existe
if (-not (Test-Path .venv)) {
    Write-Host "Création de l'environnement virtuel..."
    python -m venv .venv
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..."
.\.venv\Scripts\Activate

# Mettre à jour pip
Write-Host "Mise à jour de pip..."
python -m pip install --upgrade pip

# Installer les dépendances depuis requirements.txt
Write-Host "Installation des dépendances..."
pip install -r requirements.txt

# Télécharger le modèle spaCy
Write-Host "Téléchargement du modèle spaCy..."
python -m spacy download fr_core_news_md

Write-Host "Installation terminée avec succès!"

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
