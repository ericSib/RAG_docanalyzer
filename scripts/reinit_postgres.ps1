# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Reinitializing PostgreSQL 16..." -ForegroundColor Green

# Define paths
$PG_16_HOME = "C:\Program Files\PostgreSQL\16"
$PG_16_DATA = "$PG_16_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# Stop PostgreSQL service
Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue

# Backup old data directory if it exists
if (Test-Path $PG_16_DATA) {
    Write-Host "Backing up old data directory..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "${PG_16_DATA}_backup_${timestamp}"
    Move-Item -Path $PG_16_DATA -Destination $backupDir -Force
}

# Create new data directory
Write-Host "Creating new data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $PG_16_DATA | Out-Null

# Initialize new database cluster
Write-Host "Initializing new database cluster..." -ForegroundColor Yellow
$env:PATH = "$PG_16_HOME\bin;$env:PATH"
$initdbArgs = @(
    "--pgdata=`"$PG_16_DATA`"",
    "--encoding=UTF8",
    "--locale=French_France.1252",
    "--username=postgres",
    "--auth=trust"
)
& "$PG_16_HOME\bin\initdb.exe" $initdbArgs

# Update postgresql.conf
Write-Host "Updating postgresql.conf..." -ForegroundColor Yellow
$postgresqlConf = @"
# Add basic configuration
listen_addresses = '*'
port = 5432
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = windows
max_wal_size = 1GB
min_wal_size = 80MB
log_timezone = 'Europe/Paris'
datestyle = 'iso, dmy'
timezone = 'Europe/Paris'
lc_messages = 'French_France.1252'
lc_monetary = 'French_France.1252'
lc_numeric = 'French_France.1252'
lc_time = 'French_France.1252'
default_text_search_config = 'pg_catalog.french'

# Extension settings
dynamic_library_path = '$($PG_16_HOME -replace '\\', '/')/lib'
local_preload_libraries = ''
"@

Set-Content -Path "$PG_16_DATA\postgresql.conf" -Value $postgresqlConf

# Update pg_hba.conf for local connections
Write-Host "Updating pg_hba.conf..." -ForegroundColor Yellow
$pgHbaConf = @"
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all            all                                     trust
host    all            all             127.0.0.1/32           trust
host    all            all             ::1/128                 trust
"@

Set-Content -Path "$PG_16_DATA\pg_hba.conf" -Value $pgHbaConf

# Update service configuration
Write-Host "Updating service configuration..." -ForegroundColor Yellow
$registryPath = "HKLM:\SYSTEM\CurrentControlSet\Services\$SERVICE_NAME"
Set-ItemProperty -Path $registryPath -Name "ImagePath" -Value "`"$PG_16_HOME\bin\pg_ctl.exe`" runservice -N `"$SERVICE_NAME`" -D `"$PG_16_DATA`" -w"

# Start PostgreSQL service
Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Set postgres user password
Write-Host "Setting postgres user password..." -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"  # Le mot de passe temporaire initial
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'admin123';"

# Verify configuration
Write-Host "`nVerifying configuration:" -ForegroundColor Yellow
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "SHOW config_file; SHOW data_directory;"

Write-Host "`nReinitialization complete!" -ForegroundColor Green
Write-Host "Now you can proceed with installing the pgvector extension." -ForegroundColor Green
