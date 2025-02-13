# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Initialisation de la base de données PostgreSQL..." -ForegroundColor Yellow
Write-Host "Configuration :"
Write-Host "- Répertoire : C:\Program Files\PostgreSQL\16\data"
Write-Host "- Utilisateur : postgres"
Write-Host "- Encodage : UTF8"
Write-Host "- Authentification : trust"
Write-Host "- Locale : French_France"

& 'C:\Program Files\PostgreSQL\16\bin\initdb.exe' `
  --pgdata="C:\Program Files\PostgreSQL\16\data" `
  --username=postgres `
  --encoding=UTF8 `
  --auth=trust `
  --locale=French_France

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nInitialisation réussie !" -ForegroundColor Green
} else {
    Write-Host "`nErreur lors de l'initialisation." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
