# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Complete PostgreSQL reinstallation..." -ForegroundColor Green

# Define paths
$PG_16_HOME = "C:\Program Files\PostgreSQL\16"
$PG_16_DATA = "$PG_16_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# 1. Stop and remove service
Write-Host "Stopping and removing PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue
& sc.exe delete $SERVICE_NAME
Start-Sleep -Seconds 2

# 2. Clean registry
Write-Host "Cleaning registry..." -ForegroundColor Yellow
Remove-Item -Path "HKLM:\SOFTWARE\PostgreSQL" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Services\$SERVICE_NAME" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Backup and remove data directory
if (Test-Path $PG_16_DATA) {
    Write-Host "Backing up and removing data directory..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "${PG_16_DATA}_backup_${timestamp}"
    Move-Item -Path $PG_16_DATA -Destination $backupDir -Force
}

# 4. Initialize new database cluster
Write-Host "Initializing new database cluster..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $PG_16_DATA | Out-Null

$initdbArgs = @(
    "--pgdata=`"$PG_16_DATA`"",
    "--encoding=UTF8",
    "--locale=French_France.1252",
    "--username=postgres",
    "--auth=trust"
)
& "$PG_16_HOME\bin\initdb.exe" $initdbArgs

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

# Extension settings
dynamic_library_path = '$($PG_16_HOME -replace '\\', '/')/lib'
extension_destdir = '$($PG_16_HOME -replace '\\', '/')/share/extension'
"@

Set-Content -Path "$PG_16_DATA\postgresql.conf" -Value $postgresqlConf

# 6. Configure pg_hba.conf
Write-Host "Configuring pg_hba.conf..." -ForegroundColor Yellow
$pgHbaConf = @"
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all            all                                     trust
host    all            all             127.0.0.1/32           trust
host    all            all             ::1/128                 trust
"@

Set-Content -Path "$PG_16_DATA\pg_hba.conf" -Value $pgHbaConf

# 7. Create and start service
Write-Host "Creating and starting PostgreSQL service..." -ForegroundColor Yellow
& sc.exe create $SERVICE_NAME binPath= "`"$PG_16_HOME\bin\pg_ctl.exe`" runservice -N `"$SERVICE_NAME`" -D `"$PG_16_DATA`" -w" start= auto DisplayName= "PostgreSQL Server 16"
& sc.exe description $SERVICE_NAME "PostgreSQL Server 16"
Start-Service $SERVICE_NAME

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 8. Set postgres user password
Write-Host "Setting postgres user password..." -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'admin123';"

# 9. Verify installation
Write-Host "`nVerifying installation:" -ForegroundColor Yellow
Write-Host "`nPostgreSQL version:" -ForegroundColor Yellow
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"

Write-Host "`nConfiguration paths:" -ForegroundColor Yellow
& "$PG_16_HOME\bin\psql.exe" -U postgres -d postgres -c "SHOW config_file; SHOW data_directory;"

Write-Host "`nReinstallation complete!" -ForegroundColor Green
