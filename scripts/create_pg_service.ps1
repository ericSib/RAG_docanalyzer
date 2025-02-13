# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Creating PostgreSQL service..." -ForegroundColor Green

# Define paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# 1. Remove service if it exists
Write-Host "Removing existing service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue
& sc.exe delete $SERVICE_NAME
Start-Sleep -Seconds 2

# 2. Create service
Write-Host "Creating new service..." -ForegroundColor Yellow
& sc.exe create $SERVICE_NAME binPath= "`"$PG_HOME\bin\pg_ctl.exe`" runservice -N `"$SERVICE_NAME`" -D `"$PG_DATA`" -w" start= auto DisplayName= "PostgreSQL Server 16"
& sc.exe description $SERVICE_NAME "PostgreSQL Server 16"
Start-Sleep -Seconds 2

# 3. Start service
Write-Host "Starting service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME
Start-Sleep -Seconds 5

# 4. Verify service
Write-Host "`nVerifying service:" -ForegroundColor Yellow
Get-Service $SERVICE_NAME | Select-Object Name, Status, StartType

# 5. Test PostgreSQL connection
Write-Host "`nTesting PostgreSQL connection:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"
