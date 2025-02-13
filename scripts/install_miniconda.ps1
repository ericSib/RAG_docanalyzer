# Configuration
$minicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$installerPath = "$env:TEMP\Miniconda3-latest-Windows-x86_64.exe"

Write-Host "Installation de Miniconda..." -ForegroundColor Yellow

# Téléchargement de l'installateur
Write-Host "`n1. Téléchargement de Miniconda..."
Invoke-WebRequest -Uri $minicondaUrl -OutFile $installerPath

# Installation silencieuse
Write-Host "`n2. Installation de Miniconda..."
Start-Process -FilePath $installerPath -ArgumentList "/S /RegisterPython=1 /AddToPath=1 /InstallationType=JustMe" -Wait

# Nettoyage
Remove-Item $installerPath

Write-Host "`nMiniconda a été installé avec succès !" -ForegroundColor Green
Write-Host "Redémarrez votre terminal pour que les changements prennent effet."

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
