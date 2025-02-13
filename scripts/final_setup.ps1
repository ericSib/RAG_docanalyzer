# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Final PostgreSQL setup..." -ForegroundColor Green

# Define paths
$PG_16_HOME = "C:\Program Files\PostgreSQL\16"
$PG_16_DATA = "$PG_16_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# Stop PostgreSQL service
Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue

# Update postgresql.conf
Write-Host "Updating postgresql.conf..." -ForegroundColor Yellow
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

# Update pg_hba.conf
Write-Host "Updating pg_hba.conf..." -ForegroundColor Yellow
$pgHbaConf = @"
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all            all                                     trust
host    all            all             127.0.0.1/32           trust
host    all            all             ::1/128                 trust
"@

Set-Content -Path "$PG_16_DATA\pg_hba.conf" -Value $pgHbaConf

# Start PostgreSQL service
Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Build and install pgvector
Write-Host "Building and installing pgvector..." -ForegroundColor Yellow
$tempDir = ".\temp\pgvector_build"
$fullTempPath = (Resolve-Path ".").Path + "\temp\pgvector_build"

# Clean up existing temp directory if it exists
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Force -Recurse -ErrorAction SilentlyContinue
}

# Create fresh temp directory
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

# Clone pgvector repository
git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git .

# Set up build environment
$env:PATH = "$PG_16_HOME\bin;$env:PATH"
$env:PG_CONFIG = "$PG_16_HOME\bin\pg_config.exe"
$env:PGHOST = "localhost"
$env:PGUSER = "postgres"

# Find Visual Studio installation
$vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
$vcvarsallPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"

# Create Makefile.win
$makefileContent = @"
EXTENSION = vector
MODULE_big = vector
OBJS = src/hnsw.o src/hnswbuild.o src/hnswinsert.o src/hnswscan.o src/hnswutils.o src/hnswvacuum.o src/ivfbuild.o src/ivfflat.o src/ivfinsert.o src/ivfkmeans.o src/ivfscan.o src/ivfutils.o src/ivfvacuum.o src/vector.o
DATA = sql/vector--0.6.0.sql

PG_CONFIG = "$($env:PG_CONFIG)"
PGFILEDESC = "pgvector - vector data type and ivfflat and hnsw access methods"

REGRESS = vector ivfflat hnsw

USE_PGXS = 1

PG_CPPFLAGS = /I"$(& $env:PG_CONFIG --includedir-server)"
SHLIB_LINK = /LIBPATH:"$(& $env:PG_CONFIG --libdir)"

include $(shell "$($env:PG_CONFIG)" --pgxs)
"@

$makefileContent | Out-File -FilePath "Makefile.win" -Encoding ASCII

# Build script
$buildScript = @"
@echo off
call "$vcvarsallPath" x64
cd /d "$fullTempPath"
nmake /f Makefile.win
if errorlevel 1 exit /b 1
"@

$buildScriptPath = ".\build.bat"
$buildScript | Out-File -FilePath $buildScriptPath -Encoding ASCII

# Execute build
$buildProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $buildScriptPath -NoNewWindow -PassThru -Wait
if ($buildProcess.ExitCode -ne 0) {
    throw "Build failed"
}

# Copy files
Copy-Item "vector.dll" -Destination "$PG_16_HOME\lib" -Force
Copy-Item "sql\vector--0.6.0.sql" -Destination "$PG_16_HOME\share\extension" -Force
Copy-Item "vector.control" -Destination "$PG_16_HOME\share\extension" -Force

# Clean up
Set-Location ..
Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue

# Create database and extension
Write-Host "`nSetting up database..." -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"

# Create database if it doesn't exist
& "$PG_16_HOME\bin\createdb.exe" -U postgres rag_doc_analyzer -T template0 -E UTF8

# Create extension
& "$PG_16_HOME\bin\psql.exe" -U postgres -d rag_doc_analyzer -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify installation
Write-Host "`nVerifying installation:" -ForegroundColor Yellow
& "$PG_16_HOME\bin\psql.exe" -U postgres -d rag_doc_analyzer -c "\dx"

Write-Host "`nSetup complete!" -ForegroundColor Green
