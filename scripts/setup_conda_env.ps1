# Initialisation de conda pour PowerShell
Write-Host "Initialisation de conda pour PowerShell..." -ForegroundColor Yellow
$condaPath = "$env:USERPROFILE\miniconda3"
$condaExe = "$condaPath\Scripts\conda.exe"

if (-not (Test-Path $condaExe)) {
    Write-Host "Erreur : Miniconda n'est pas installé dans le répertoire par défaut." -ForegroundColor Red
    Write-Host "Veuillez d'abord installer Miniconda : https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Red
    exit 1
}

# Initialisation de conda
& "$condaPath\shell\condabin\conda-hook.ps1"
conda activate

# Création de l'environnement conda
Write-Host "`nCréation de l'environnement conda rag..." -ForegroundColor Yellow
conda create -n rag python=3.9 -y

# Activation de l'environnement
Write-Host "`nActivation de l'environnement rag..." -ForegroundColor Yellow
conda activate rag

Write-Host "`nEnvironnement conda créé et activé avec succès !" -ForegroundColor Green

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
