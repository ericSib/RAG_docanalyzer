# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Installing pgvector from zip..." -ForegroundColor Green

# Define paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_SHARE = "$PG_HOME\share"
$PG_LIB = "$PG_HOME\lib"
$PG_EXTENSION = "$PG_SHARE\extension"
$ZIP_PATH = "C:\Program Files\PostgreSQL\pgvector-master.zip"
$TEMP_DIR = ".\temp\pgvector_build"

# Create temp directory
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null
Set-Location $TEMP_DIR

try {
    # Extract zip
    Write-Host "Extracting pgvector source..." -ForegroundColor Yellow
    Expand-Archive -Path $ZIP_PATH -DestinationPath "." -Force

    Set-Location "pgvector-master"

    # Set up environment
    $env:PATH = "$PG_HOME\bin;$env:PATH"
    $env:PG_CONFIG = "$PG_HOME\bin\pg_config.exe"
    
    # Find Visual Studio
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

    # Create build script
    $buildScript = @"
@echo off
call "$vcvarsallPath" x64
nmake /f Makefile.win
if errorlevel 1 exit /b 1
"@

    $buildScriptPath = ".\build.bat"
    $buildScript | Out-File -FilePath $buildScriptPath -Encoding ASCII

    # Build
    Write-Host "Building pgvector..." -ForegroundColor Yellow
    cmd /c build.bat

    # Copy files
    Write-Host "Installing files..." -ForegroundColor Yellow
    
    Write-Host "Copying vector.dll to $PG_LIB..." -ForegroundColor Yellow
    Copy-Item -Path "vector.dll" -Destination "$PG_LIB" -Force -Verbose
    
    Write-Host "Copying SQL file to $PG_EXTENSION..." -ForegroundColor Yellow
    Copy-Item -Path "sql\vector--0.6.0.sql" -Destination "$PG_EXTENSION" -Force -Verbose
    
    Write-Host "Copying control file to $PG_EXTENSION..." -ForegroundColor Yellow
    Copy-Item -Path "vector.control" -Destination "$PG_EXTENSION" -Force -Verbose

    # Verify files
    Write-Host "`nVerifying installed files:" -ForegroundColor Yellow
    if (Test-Path "$PG_LIB\vector.dll") {
        Write-Host "vector.dll is present" -ForegroundColor Green
    } else {
        Write-Host "vector.dll is missing!" -ForegroundColor Red
    }

    if (Test-Path "$PG_EXTENSION\vector--0.6.0.sql") {
        Write-Host "vector--0.6.0.sql is present" -ForegroundColor Green
    } else {
        Write-Host "vector--0.6.0.sql is missing!" -ForegroundColor Red
    }

    if (Test-Path "$PG_EXTENSION\vector.control") {
        Write-Host "vector.control is present" -ForegroundColor Green
    } else {
        Write-Host "vector.control is missing!" -ForegroundColor Red
    }

    # Create extension
    Write-Host "`nCreating extension..." -ForegroundColor Yellow
    $env:PGPASSWORD = "admin123"
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "DROP EXTENSION IF EXISTS vector;"
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "CREATE EXTENSION vector;"

    # Verify installation
    Write-Host "`nVerifying installation:" -ForegroundColor Yellow
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "\dx vector"

} catch {
    Write-Error "An error occurred: $_"
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    throw
} finally {
    # Clean up
    Set-Location ..\..
    Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
}
