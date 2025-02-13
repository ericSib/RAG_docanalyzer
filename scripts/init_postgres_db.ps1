# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Initializing PostgreSQL database..." -ForegroundColor Green

# Define paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# 1. Stop service if running
Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 2. Backup existing data directory if it exists
if (Test-Path $PG_DATA) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "${PG_DATA}_backup_${timestamp}"
    Write-Host "Backing up existing data directory to: $backupDir" -ForegroundColor Yellow
    Move-Item -Path $PG_DATA -Destination $backupDir -Force
}

# 3. Create new data directory
Write-Host "Creating new data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $PG_DATA | Out-Null

# 4. Initialize database cluster
Write-Host "Initializing database cluster..." -ForegroundColor Yellow
$initdbArgs = @(
    "--pgdata=`"$PG_DATA`"",
    "--encoding=UTF8",
    "--locale=French_France.1252",
    "--username=postgres",
    "--auth=trust"
)
& "$PG_HOME\bin\initdb.exe" $initdbArgs

# 5. Configure postgresql.conf
Write-Host "Configuring postgresql.conf..." -ForegroundColor Yellow
$postgresqlConf = @"
# PostgreSQL configuration file
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
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 10MB
"@

Set-Content -Path "$PG_DATA\postgresql.conf" -Value $postgresqlConf

# 6. Configure pg_hba.conf
Write-Host "Configuring pg_hba.conf..." -ForegroundColor Yellow
$pgHbaConf = @"
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all            all                                     trust
host    all            all             127.0.0.1/32           trust
host    all            all             ::1/128                 trust
"@

Set-Content -Path "$PG_DATA\pg_hba.conf" -Value $pgHbaConf

# 7. Start service
Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME
Start-Sleep -Seconds 5

# 8. Set postgres user password
Write-Host "Setting postgres user password..." -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'admin123';"

# 9. Verify installation
Write-Host "`nVerifying installation:" -ForegroundColor Yellow
Write-Host "`nPostgreSQL version:" -ForegroundColor Yellow
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"

Write-Host "`nConfiguration paths:" -ForegroundColor Yellow
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "SHOW config_file; SHOW data_directory;"

Write-Host "`nInitialization complete!" -ForegroundColor Green
