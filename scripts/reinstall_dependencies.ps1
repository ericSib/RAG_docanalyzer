# Désinstallation des packages existants
Write-Host "Désinstallation des packages existants..." -ForegroundColor Yellow
pip uninstall -y torch sentence-transformers

# Installation de PyTorch
Write-Host "`nInstallation de PyTorch..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Installation des autres dépendances
Write-Host "`nInstallation des autres packages..." -ForegroundColor Yellow
pip install sentence-transformers spacy sqlalchemy psycopg2-binary tqdm

# Installation du modèle français Spacy
Write-Host "`nInstallation du modèle français Spacy..." -ForegroundColor Yellow
python -m spacy download fr_core_news_md

Write-Host "`nDépendances réinstallées avec succès !" -ForegroundColor Green

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
