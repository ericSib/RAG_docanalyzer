# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Restarting PostgreSQL service..." -ForegroundColor Green

$SERVICE_NAME = "postgresql-x64-16"
$PG_HOME = "C:\Program Files\PostgreSQL\16"

# 1. Check service status
Write-Host "Current service status:" -ForegroundColor Yellow
Get-Service $SERVICE_NAME | Select-Object Name, Status, StartType

# 2. Stop service
Write-Host "`nStopping service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 3. Start service
Write-Host "Starting service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME
Start-Sleep -Seconds 5

# 4. Check final status
Write-Host "`nFinal service status:" -ForegroundColor Yellow
Get-Service $SERVICE_NAME | Select-Object Name, Status, StartType

# 5. Test PostgreSQL connection
Write-Host "`nTesting PostgreSQL connection:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"
