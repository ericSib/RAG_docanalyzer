# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Cleaning PostgreSQL installation..." -ForegroundColor Green

# Define paths
$PG_16_HOME = "C:\Program Files\PostgreSQL\16"
$SERVICE_NAME = "postgresql-x64-16"

# 1. Stop PostgreSQL service
Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue

# 2. Remove service
Write-Host "Removing PostgreSQL service..." -ForegroundColor Yellow
& sc.exe delete $SERVICE_NAME
Start-Sleep -Seconds 2

# 3. Clean registry
Write-Host "Cleaning registry..." -ForegroundColor Yellow

# Backup registry first
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = ".\PostgreSQL_registry_backup_$timestamp.reg"
reg export "HKLM\SOFTWARE\PostgreSQL" $backupFile /y

# Remove PostgreSQL registry keys
Remove-Item -Path "HKLM:\SOFTWARE\PostgreSQL" -Recurse -Force -ErrorAction SilentlyContinue

# 4. Create new service with correct paths
Write-Host "Creating new PostgreSQL service..." -ForegroundColor Yellow
& sc.exe create $SERVICE_NAME binPath= "`"$PG_16_HOME\bin\pg_ctl.exe`" runservice -N `"$SERVICE_NAME`" -D `"$PG_16_HOME\data`" -w" start= auto DisplayName= "PostgreSQL Server 16"
& sc.exe description $SERVICE_NAME "PostgreSQL Server 16"

# 5. Start service
Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME
Start-Sleep -Seconds 5

# 6. Verify installation
Write-Host "`nVerifying PostgreSQL installation:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
Write-Host "`nChecking PostgreSQL version:" -ForegroundColor Yellow
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"

Write-Host "`nChecking configuration paths:" -ForegroundColor Yellow
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "SHOW config_file; SHOW data_directory;"

Write-Host "`nCleaning complete!" -ForegroundColor Green
Write-Host "A backup of the registry has been saved to: $backupFile" -ForegroundColor Green
