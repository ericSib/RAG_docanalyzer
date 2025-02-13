# Désinstallation complète de PyTorch
Write-Host "Désinstallation de PyTorch..." -ForegroundColor Yellow
pip uninstall -y torch torchvision torchaudio

# Installation de PyTorch avec des options spécifiques
Write-Host "`nInstallation de PyTorch..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --no-cache-dir

Write-Host "`nPyTorch a été réinstallé avec succès !" -ForegroundColor Green

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
