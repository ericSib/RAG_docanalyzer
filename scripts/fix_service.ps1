# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Fixing PostgreSQL service configuration..." -ForegroundColor Green

# Define paths
$PG_16_HOME = "C:\Program Files\PostgreSQL\16"
$PG_16_DATA = "$PG_16_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# Stop PostgreSQL service
Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue

# Remove existing service
Write-Host "Removing existing PostgreSQL service..." -ForegroundColor Yellow
& sc.exe delete $SERVICE_NAME

# Wait for service removal
Start-Sleep -Seconds 2

# Create new service with correct path
Write-Host "Creating new PostgreSQL service with correct paths..." -ForegroundColor Yellow
& sc.exe create $SERVICE_NAME binPath= "`"$PG_16_HOME\bin\pg_ctl.exe`" runservice -N `"$SERVICE_NAME`" -D `"$PG_16_DATA`" -w" start= auto DisplayName= "PostgreSQL Server 16"

# Set service description
& sc.exe description $SERVICE_NAME "PostgreSQL Server 16"

# Start the service
Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify configuration
Write-Host "`nVerifying configuration:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "SHOW config_file; SHOW data_directory;"

Write-Host "`nService configuration updated!" -ForegroundColor Green
