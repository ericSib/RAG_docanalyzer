# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$serviceName = "postgresql-x64-16"

Write-Host "Arrêt du service PostgreSQL..." -ForegroundColor Yellow
Stop-Service $serviceName -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Démarrage du service PostgreSQL..." -ForegroundColor Yellow
Start-Service $serviceName

Write-Host "Vérification du statut..." -ForegroundColor Yellow
Get-Service $serviceName | Select-Object Name, DisplayName, Status

Write-Host "Appuyez sur une touche pour continuer..."
pause
