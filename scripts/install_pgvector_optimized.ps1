# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

# Load configuration
$configPath = Join-Path $PSScriptRoot "..\config\versions.json"
if (-not (Test-Path $configPath)) {
    throw "Configuration file not found at: $configPath"
}

$config = Get-Content $configPath | ConvertFrom-Json

# Validate PostgreSQL installation
function Test-PostgresInstallation {
    param (
        $config
    )
    
    $pgHome = $config.postgresql.installPath
    if (-not (Test-Path $pgHome)) {
        throw "PostgreSQL installation not found at: $pgHome"
    }

    $pgVersion = & "$pgHome\bin\psql.exe" -V
    if (-not $pgVersion) {
        throw "Could not determine PostgreSQL version"
    }

    Write-Host "Found PostgreSQL: $pgVersion" -ForegroundColor Green
    return $true
}

# Validate Visual Studio installation
function Test-VisualStudio {
    $vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
    if (-not $vsPath) {
        throw "Visual Studio installation not found. Required for building pgvector."
    }

    $vcvarsallPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"
    if (-not (Test-Path $vcvarsallPath)) {
        throw "Visual Studio C++ build tools not found."
    }

    Write-Host "Found Visual Studio at: $vsPath" -ForegroundColor Green
    return $vcvarsallPath
}

# Build pgvector
function Build-PgVector {
    param (
        $config,
        $vcvarsallPath,
        $buildDir
    )

    # Create Makefile.win
    $makefileContent = @"
EXTENSION = vector
MODULE_big = vector
OBJS = src/hnsw.o src/hnswbuild.o src/hnswinsert.o src/hnswscan.o src/hnswutils.o src/hnswvacuum.o src/ivfbuild.o src/ivfflat.o src/ivfinsert.o src/ivfkmeans.o src/ivfscan.o src/ivfutils.o src/ivfvacuum.o src/vector.o
DATA = sql/vector--$($config.pgvector.version).sql

PG_CONFIG = "$($config.postgresql.installPath)\bin\pg_config.exe"
PGFILEDESC = "pgvector - vector data type and ivfflat and hnsw access methods"

REGRESS = vector ivfflat hnsw

USE_PGXS = 1

PG_CPPFLAGS = /I"$(& "$($config.postgresql.installPath)\bin\pg_config.exe" --includedir-server)"
SHLIB_LINK = /LIBPATH:"$(& "$($config.postgresql.installPath)\bin\pg_config.exe" --libdir)"

include $(shell "$($config.postgresql.installPath)\bin\pg_config.exe" --pgxs)
"@

    $makefileContent | Out-File -FilePath "$buildDir\Makefile.win" -Encoding ASCII

    # Create build script
    $buildScript = @"
@echo off
call "$vcvarsallPath" x64
nmake /f Makefile.win
if errorlevel 1 exit /b 1
"@

    $buildScript | Out-File -FilePath "$buildDir\build.bat" -Encoding ASCII

    # Execute build
    Write-Host "Building pgvector..." -ForegroundColor Yellow
    Push-Location $buildDir
    try {
        $buildProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "build.bat" -NoNewWindow -PassThru -Wait
        if ($buildProcess.ExitCode -ne 0) {
            throw "Build failed with exit code: $($buildProcess.ExitCode)"
        }
    } finally {
        Pop-Location
    }
}

# Install pgvector files
function Install-PgVector {
    param (
        $config,
        $buildDir
    )

    $pgExtension = Join-Path $config.postgresql.installPath "share\extension"
    $pgLib = Join-Path $config.postgresql.installPath "lib"

    # Create directories if they don't exist
    New-Item -ItemType Directory -Force -Path $pgExtension | Out-Null
    New-Item -ItemType Directory -Force -Path $pgLib | Out-Null

    # Copy files
    Write-Host "Installing pgvector files..." -ForegroundColor Yellow
    
    $dllSource = Join-Path $buildDir $config.pgvector.files.dll
    $sqlSource = Join-Path $buildDir "sql\$($config.pgvector.files.sql)"
    $controlSource = Join-Path $buildDir $config.pgvector.files.control

    Copy-Item -Path $dllSource -Destination $pgLib -Force -Verbose
    Copy-Item -Path $sqlSource -Destination $pgExtension -Force -Verbose
    Copy-Item -Path $controlSource -Destination $pgExtension -Force -Verbose

    # Verify installation
    $files = @(
        (Join-Path $pgLib $config.pgvector.files.dll),
        (Join-Path $pgExtension $config.pgvector.files.sql),
        (Join-Path $pgExtension $config.pgvector.files.control)
    )

    foreach ($file in $files) {
        if (-not (Test-Path $file)) {
            throw "Installation failed: $file not found"
        }
    }
}

# Create database extension
function Install-DatabaseExtension {
    param (
        $config
    )

    $env:PGPASSWORD = "admin123"
    $psql = Join-Path $config.postgresql.installPath "bin\psql.exe"

    Write-Host "Creating pgvector extension in database..." -ForegroundColor Yellow
    & $psql -U postgres -d postgres -c "DROP EXTENSION IF EXISTS vector;"
    & $psql -U postgres -d postgres -c "CREATE EXTENSION vector;"

    # Verify extension
    $result = & $psql -U postgres -d postgres -c "\dx vector"
    if ($result -notmatch "vector") {
        throw "Extension installation failed"
    }
}

try {
    Write-Host "Starting pgvector installation..." -ForegroundColor Green

    # Validate environment
    Test-PostgresInstallation $config
    $vcvarsallPath = Test-VisualStudio

    # Prepare build directory
    $buildDir = Join-Path $PSScriptRoot "..\temp\pgvector_build"
    New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
    
    # Clone repository
    Write-Host "Cloning pgvector repository..." -ForegroundColor Yellow
    Push-Location $buildDir
    try {
        git clone --branch $config.pgvector.gitTag https://github.com/pgvector/pgvector.git .
    } finally {
        Pop-Location
    }

    # Build and install
    Build-PgVector $config $vcvarsallPath $buildDir
    Install-PgVector $config $buildDir
    Install-DatabaseExtension $config

    Write-Host "`nInstallation completed successfully!" -ForegroundColor Green

} catch {
    Write-Error "Installation failed: $_"
    throw
} finally {
    # Cleanup
    if (Test-Path $buildDir) {
        Remove-Item -Recurse -Force $buildDir -ErrorAction SilentlyContinue
    }
}
