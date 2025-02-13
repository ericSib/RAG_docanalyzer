# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$serviceName = "postgresql-x64-16"
$displayName = "PostgreSQL 16 Server"
$binaryPath = "`"C:\Program Files\PostgreSQL\16\bin\postgres.exe`" `"--config-file=C:\Program Files\PostgreSQL\16\data\postgresql.conf`" `"-D C:\Program Files\PostgreSQL\16\data`""

Write-Host "Suppression de l'ancien service s'il existe..." -ForegroundColor Yellow
sc.exe delete $serviceName

Write-Host "Création du service PostgreSQL..." -ForegroundColor Yellow
sc.exe create $serviceName binPath= $binaryPath DisplayName= $displayName start= auto obj= "NT AUTHORITY\NetworkService"

Write-Host "Configuration des dépendances..." -ForegroundColor Yellow
sc.exe config $serviceName depend= Tcpip/Afd

Write-Host "Démarrage du service..." -ForegroundColor Yellow
Start-Service $serviceName

Write-Host "Vérification du statut..." -ForegroundColor Yellow
Get-Service $serviceName | Select-Object Name, DisplayName, Status

Write-Host "Configuration terminée !" -ForegroundColor Green

pause
