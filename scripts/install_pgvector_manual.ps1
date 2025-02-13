# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Manual pgvector installation..." -ForegroundColor Green

# Define paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_SHARE = "$PG_HOME\share"
$PG_LIB = "$PG_HOME\lib"
$PG_EXTENSION = "$PG_SHARE\extension"

# Create temp directory
$tempDir = ".\temp\pgvector_build"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

try {
    # Clone pgvector
    Write-Host "Cloning pgvector repository..." -ForegroundColor Yellow
    git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git .

    # Set up environment
    $env:PATH = "$PG_HOME\bin;$env:PATH"
    $env:PG_CONFIG = "$PG_HOME\bin\pg_config.exe"
    
    # Find Visual Studio
    $vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
    $vcvarsallPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"

    # Create a simple test program to verify vector.dll compilation
    $testProgram = @"
#include "postgres.h"
#include "fmgr.h"
#include "utils/array.h"
#include "catalog/pg_type.h"

PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(vector_in);

Datum vector_in(PG_FUNCTION_ARGS)
{
    return (Datum) 0;
}
"@

    Set-Content -Path "test.c" -Value $testProgram

    # Create a simplified Makefile
    $makefileContent = @"
MODULES = vector
EXTENSION = vector
DATA = sql/vector--0.6.0.sql
PG_CONFIG = $env:PG_CONFIG

ifdef USE_PGXS
PG_CONFIG = $env:PG_CONFIG
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
endif

SRCS = src/hnsw.c src/hnswbuild.c src/hnswinsert.c src/hnswscan.c src/hnswutils.c src/hnswvacuum.c src/ivfbuild.c src/ivfflat.c src/ivfinsert.c src/ivfkmeans.c src/ivfscan.c src/ivfutils.c src/ivfvacuum.c src/vector.c

OBJS = $(SRCS:.c=.o)

PG_CPPFLAGS = -I$(shell $(PG_CONFIG) --includedir)
SHLIB_LINK = -L$(shell $(PG_CONFIG) --libdir) -lpostgres

all: vector.dll

vector.dll: $(OBJS)
	link /DLL /OUT:vector.dll $(OBJS) $(SHLIB_LINK)

.c.o:
	cl /c $(PG_CPPFLAGS) $<

clean:
	del /F /Q *.o *.dll
"@

    Set-Content -Path "Makefile" -Value $makefileContent

    # Create build script
    $buildScript = @"
@echo off
call "$vcvarsallPath" x64
nmake /f Makefile
"@

    Set-Content -Path "build.bat" -Value $buildScript -Encoding ASCII

    # Build
    Write-Host "Building pgvector..." -ForegroundColor Yellow
    cmd /c build.bat

    # Copy files
    Write-Host "Installing files..." -ForegroundColor Yellow
    
    # Create extension directory if it doesn't exist
    if (-not (Test-Path $PG_EXTENSION)) {
        New-Item -ItemType Directory -Force -Path $PG_EXTENSION | Out-Null
    }

    # Copy with verbose output
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
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
}
