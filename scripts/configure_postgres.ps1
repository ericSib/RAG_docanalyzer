# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Configuring PostgreSQL..." -ForegroundColor Green

$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"
$PG_CONF = "$PG_DATA\postgresql.conf"

# Update postgresql.conf
Write-Host "Updating postgresql.conf..." -ForegroundColor Yellow
$confContent = @"
# Add these lines at the end of postgresql.conf
dynamic_library_path = '$($PG_HOME -replace '\\', '/')/lib'
extension_destdir = '$($PG_HOME -replace '\\', '/')/share/extension'
"@

Add-Content -Path $PG_CONF -Value "`n$confContent"

# Restart PostgreSQL service
Write-Host "Restarting PostgreSQL service..." -ForegroundColor Yellow
Stop-Service postgresql-x64-16 -Force
Start-Service postgresql-x64-16

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Create the extension
Write-Host "Creating pgvector extension..." -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"  # Replace with your actual password
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify installation
Write-Host "`nVerifying installation:" -ForegroundColor Yellow
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "\dx"

Write-Host "`nConfiguration complete!" -ForegroundColor Green
