# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "Suppression de l'ancien service s'il existe..." -ForegroundColor Yellow
$oldServices = Get-Service | Where-Object {$_.Name -like "*PostgreSQL*" -or $_.Name -like "*postgres*"}
foreach ($service in $oldServices) {
    Write-Host "Suppression du service : $($service.Name)"
    sc.exe delete $service.Name
}

Write-Host "`nInstallation du nouveau service..." -ForegroundColor Yellow
& 'C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe' register `
  -N "PostgreSQL_16" `
  -D "C:\Program Files\PostgreSQL\16\data"

Write-Host "`nConfiguration du service..." -ForegroundColor Yellow
Set-Service -Name "PostgreSQL_16" `
  -StartupType Automatic `
  -Description "PostgreSQL Database Server 16"

Write-Host "`nDémarrage du service..." -ForegroundColor Yellow
Start-Service -Name "PostgreSQL_16"

Write-Host "`nStatut du service :" -ForegroundColor Yellow
Get-Service -Name "PostgreSQL_16" | Select-Object Name, Status, StartType

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
