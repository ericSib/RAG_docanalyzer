# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$env:PATH = "C:\Program Files\PostgreSQL\16\bin;$env:PATH"

Write-Host "Suppression de l'ancien service s'il existe..." -ForegroundColor Yellow
pg_ctl.exe unregister -N "postgresql-x64-16" -s

Write-Host "Enregistrement du service PostgreSQL..." -ForegroundColor Yellow
pg_ctl.exe register -N "postgresql-x64-16" -D "C:\Program Files\PostgreSQL\16\data" -S auto -U "NT AUTHORITY\NetworkService"

Write-Host "Démarrage du service..." -ForegroundColor Yellow
Start-Service postgresql-x64-16

Write-Host "Configuration terminée !" -ForegroundColor Green

pause
