# Installation de PyTorch avec CUDA
Write-Host "Installation de PyTorch avec CUDA..." -ForegroundColor Yellow
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Installation de sentence-transformers
Write-Host "`nInstallation de sentence-transformers..." -ForegroundColor Yellow
pip install sentence-transformers

# Installation des autres dépendances
Write-Host "`nInstallation des autres dépendances..." -ForegroundColor Yellow
pip install spacy sqlalchemy psycopg2-binary tqdm

# Installation du modèle français spaCy
Write-Host "`nInstallation du modèle français spaCy..." -ForegroundColor Yellow
python -m spacy download fr_core_news_md

Write-Host "`nToutes les dépendances ont été installées avec succès !" -ForegroundColor Green

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
