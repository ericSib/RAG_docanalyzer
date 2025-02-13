# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Installing pgvector using MSVC..." -ForegroundColor Green

# Set PostgreSQL paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_SHARE = "$PG_HOME\share"
$PG_LIB = "$PG_HOME\lib"
$PG_EXTENSION = "$PG_SHARE\extension"
$PG_DATA = "$PG_HOME\data"

# Verify PostgreSQL installation
if (-not (Test-Path $PG_HOME)) {
    throw "PostgreSQL 16 installation not found at: $PG_HOME"
}

# Use a temp directory in the project folder
$tempDir = ".\temp\pgvector_build"
$fullTempPath = (Resolve-Path ".").Path + "\temp\pgvector_build"

# Clean up existing temp directory if it exists
if (Test-Path $tempDir) {
    Write-Host "Cleaning up existing temp directory..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $tempDir -Force -Recurse -ErrorAction SilentlyContinue
    } catch {
        Write-Warning "Could not fully clean temp directory. Continuing anyway..."
    }
}

# Create fresh temp directory
Write-Host "Creating temp directory..." -ForegroundColor Yellow
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
    $env:PGHOST = "localhost"
    $env:PGUSER = "postgres"
    
    # Find Visual Studio installation
    Write-Host "Looking for Visual Studio installation..." -ForegroundColor Yellow
    $vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
    if (-not $vsPath) {
        throw "Visual Studio installation not found"
    }
    Write-Host "Found Visual Studio at: $vsPath" -ForegroundColor Green
    
    $vcvarsallPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"
    Write-Host "Using vcvarsall.bat from: $vcvarsallPath" -ForegroundColor Green

    # Create a modified Makefile.win
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

    # Initialize Visual Studio environment for x64
    Write-Host "Setting up Visual Studio environment..." -ForegroundColor Yellow
    $buildScript = @"
@echo off
call "$vcvarsallPath" x64
cd /d "$fullTempPath"
nmake /f Makefile.win
if errorlevel 1 exit /b 1
"@

    $buildScriptPath = ".\build.bat"
    $buildScript | Out-File -FilePath $buildScriptPath -Encoding ASCII
    
    # Execute the build script
    Write-Host "Building pgvector..." -ForegroundColor Yellow
    $buildProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $buildScriptPath -NoNewWindow -PassThru -Wait -RedirectStandardOutput ".\build.log" -RedirectStandardError ".\build.error.log"

    if ($buildProcess.ExitCode -ne 0) {
        $buildLog = Get-Content ".\build.log" -ErrorAction SilentlyContinue
        $buildErrorLog = Get-Content ".\build.error.log" -ErrorAction SilentlyContinue
        Write-Host "Build log:" -ForegroundColor Red
        $buildLog | ForEach-Object { Write-Host $_ }
        Write-Host "Build error log:" -ForegroundColor Red
        $buildErrorLog | ForEach-Object { Write-Host $_ }
        throw "Build failed with exit code $($buildProcess.ExitCode)"
    }

    Write-Host "Build completed successfully." -ForegroundColor Green
    
    # Manually copy files to correct locations
    Write-Host "Installing files..." -ForegroundColor Yellow
    
    # Create extension directory if it doesn't exist
    if (-not (Test-Path $PG_EXTENSION)) {
        New-Item -ItemType Directory -Force -Path $PG_EXTENSION | Out-Null
    }
    
    # Copy DLL
    Write-Host "Copying vector.dll to $PG_LIB..." -ForegroundColor Yellow
    Copy-Item "vector.dll" -Destination "$PG_LIB" -Force
    
    # Copy SQL and control files
    Write-Host "Copying SQL and control files to $PG_EXTENSION..." -ForegroundColor Yellow
    Copy-Item "sql\vector--0.6.0.sql" -Destination "$PG_EXTENSION" -Force
    Copy-Item "vector.control" -Destination "$PG_EXTENSION" -Force

    # Verify files were copied correctly
    Write-Host "Verifying installed files..." -ForegroundColor Yellow
    $missingFiles = @()
    
    if (-not (Test-Path "$PG_LIB\vector.dll")) { $missingFiles += "vector.dll" }
    if (-not (Test-Path "$PG_EXTENSION\vector--0.6.0.sql")) { $missingFiles += "vector--0.6.0.sql" }
    if (-not (Test-Path "$PG_EXTENSION\vector.control")) { $missingFiles += "vector.control" }
    
    if ($missingFiles.Count -gt 0) {
        throw "Missing files after installation: $($missingFiles -join ', ')"
    }
    
    Write-Host "All files installed correctly." -ForegroundColor Green

    # Update postgresql.conf if needed
    $postgresqlConf = "$PG_DATA\postgresql.conf"
    $confContent = Get-Content $postgresqlConf -Raw
    if ($confContent -notmatch 'dynamic_library_path') {
        Write-Host "Adding dynamic_library_path to postgresql.conf..." -ForegroundColor Yellow
        Add-Content $postgresqlConf "`ndynamic_library_path = '$PG_LIB'"
    }

    Write-Host "Installation completed." -ForegroundColor Green
    Write-Host "Restarting PostgreSQL service..." -ForegroundColor Yellow

    # Restart PostgreSQL service
    $serviceName = "postgresql-x64-16"
    Stop-Service -Name $serviceName -Force
    Start-Service -Name $serviceName

    Write-Host "PostgreSQL service restarted successfully." -ForegroundColor Green
    Start-Sleep -Seconds 5  # Give the service time to fully start

    # Verify installation
    Write-Host "Verifying pgvector installation..." -ForegroundColor Yellow
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

    # Show detailed extension information
    Write-Host "`nChecking installed extensions:" -ForegroundColor Yellow
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "\dx"

} catch {
    Write-Error "An error occurred: $_"
    if (Test-Path ".\build.log") {
        Write-Host "Build log:" -ForegroundColor Yellow
        Get-Content ".\build.log"
    }
    if (Test-Path ".\build.error.log") {
        Write-Host "Build error log:" -ForegroundColor Red
        Get-Content ".\build.error.log"
    }
    throw
} finally {
    # Clean up
    Set-Location ..
    if (Test-Path $tempDir) {
        Write-Host "Cleaning up..." -ForegroundColor Yellow
        try {
            Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
        } catch {
            Write-Warning "Could not clean up temp directory. You may want to delete it manually: $tempDir"
        }
    }
}
