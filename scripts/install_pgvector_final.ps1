# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Installing pgvector..." -ForegroundColor Green

# Define paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_SHARE = "$PG_HOME\share"
$PG_LIB = "$PG_HOME\lib"
$PG_EXTENSION = "$PG_SHARE\extension"

# Use a temp directory in the project folder
$tempDir = ".\temp\pgvector_build"
$fullTempPath = (Resolve-Path ".").Path + "\temp\pgvector_build"

# Clean up existing temp directory if it exists
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Force -Recurse -ErrorAction SilentlyContinue
}

# Create fresh temp directory
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

try {
    # Clone pgvector repository
    Write-Host "Cloning pgvector repository..." -ForegroundColor Yellow
    git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git .

    # Set up build environment
    Write-Host "Setting up build environment..." -ForegroundColor Yellow
    $env:PATH = "$PG_HOME\bin;$env:PATH"
    $env:PG_CONFIG = "$PG_HOME\bin\pg_config.exe"
    
    # Find Visual Studio installation
    Write-Host "Looking for Visual Studio installation..." -ForegroundColor Yellow
    $vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
    if (-not $vsPath) {
        throw "Visual Studio installation not found"
    }
    
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
    Write-Host "Building pgvector..." -ForegroundColor Yellow
    $buildProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $buildScriptPath -NoNewWindow -PassThru -Wait
    if ($buildProcess.ExitCode -ne 0) {
        throw "Build failed"
    }

    # Copy files
    Write-Host "Installing files..." -ForegroundColor Yellow
    Copy-Item "vector.dll" -Destination "$PG_LIB" -Force
    Copy-Item "sql\vector--0.6.0.sql" -Destination "$PG_EXTENSION" -Force
    Copy-Item "vector.control" -Destination "$PG_EXTENSION" -Force

    Write-Host "Installation completed." -ForegroundColor Green

    # Create extension in database
    Write-Host "Creating extension in database..." -ForegroundColor Yellow
    $env:PGPASSWORD = "admin123"
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

    # Verify installation
    Write-Host "`nVerifying installation:" -ForegroundColor Yellow
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "\dx vector"

} catch {
    Write-Error "An error occurred: $_"
    throw
} finally {
    # Clean up
    Set-Location ..
    if (Test-Path $tempDir) {
        Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    }
}
