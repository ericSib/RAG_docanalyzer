# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "Arrêt des processus PostgreSQL..." -ForegroundColor Yellow
Stop-Process -Name postgres -Force -ErrorAction SilentlyContinue

# Backup existing data directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dataDir = "C:\Program Files\PostgreSQL\16\data"
$backupDir = "C:\Program Files\PostgreSQL\16\data_backup_$timestamp"

Write-Host "Sauvegarde du répertoire data vers $backupDir..." -ForegroundColor Yellow
if (Test-Path $dataDir) {
    Move-Item -Path $dataDir -Destination $backupDir -Force
}

Write-Host "Création d'un nouveau répertoire data..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null

Write-Host "Initialisation de la base de données..." -ForegroundColor Yellow
& 'C:\Program Files\PostgreSQL\16\bin\initdb.exe' `
  -D $dataDir `
  -U postgres `
  --encoding=UTF8 `
  --locale=French_France

Write-Host "Opération terminée !" -ForegroundColor Green
Write-Host "Une sauvegarde de l'ancien répertoire data a été créée dans : $backupDir" -ForegroundColor Yellow

pause
