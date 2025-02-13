# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Fixing PostgreSQL paths..." -ForegroundColor Green

# Define paths
$PG_16_HOME = "C:\Program Files\PostgreSQL\16"
$PG_16_DATA = "$PG_16_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# Stop PostgreSQL service
Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force

# Update registry
Write-Host "Updating registry..." -ForegroundColor Yellow
$registryPath = "HKLM:\SYSTEM\CurrentControlSet\Services\$SERVICE_NAME"
Set-ItemProperty -Path $registryPath -Name "ImagePath" -Value "`"$PG_16_HOME\bin\pg_ctl.exe`" runservice -N `"$SERVICE_NAME`" -D `"$PG_16_DATA`" -w"

# Start PostgreSQL service
Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify configuration
Write-Host "`nVerifying configuration:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"  # Remplacez par votre mot de passe
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "SHOW config_file; SHOW data_directory;"

Write-Host "`nPath correction complete!" -ForegroundColor Green
