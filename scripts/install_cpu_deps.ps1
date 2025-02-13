# Augmentation du timeout de pip
$Env:PIP_DEFAULT_TIMEOUT = 100

Write-Host "Installation de PyTorch (CPU)..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

Write-Host "`nInstallation de sentence-transformers..." -ForegroundColor Yellow
pip install sentence-transformers

Write-Host "`nInstallation de spaCy..." -ForegroundColor Yellow
pip install spacy

Write-Host "`nTéléchargement du modèle français spaCy..." -ForegroundColor Yellow
python -m spacy download fr_core_news_md

Write-Host "`nInstallation des autres dépendances..." -ForegroundColor Yellow
pip install sqlalchemy psycopg2-binary tqdm

Write-Host "`nVérification des imports..." -ForegroundColor Yellow
python -c "import torch; import sentence_transformers; import spacy; print('Tous les imports fonctionnent!')"

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
