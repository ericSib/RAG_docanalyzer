# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Installing pgvector..." -ForegroundColor Green

# Find Visual Studio installation using vswhere
$vswherePath = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $vswherePath)) {
    Write-Host "Visual Studio Installer not found. Please run Visual Studio Installer first." -ForegroundColor Red
    exit 1
}

Write-Host "Looking for Visual Studio installation..." -ForegroundColor Yellow
$vsPath = & $vswherePath -all -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vsPath) {
    Write-Host "Visual Studio with C++ tools not found." -ForegroundColor Red
    Write-Host "Please install the 'Desktop development with C++' workload." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Visual Studio at: $vsPath" -ForegroundColor Green

# Set up environment
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$env:PATH = "$PG_HOME\bin;$env:PATH"
$env:PGPASSWORD = "admin123"
$env:PGROOT = $PG_HOME
$env:PGBIN = "$PG_HOME\bin"
$env:PGLIB = "$PG_HOME\lib"
$env:PGINCLUDE = "$PG_HOME\include"

# Create temp directory
$tempDir = ".\temp\pgvector_build"
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Push-Location $tempDir

try {
    # Clone pgvector
    Write-Host "Cloning pgvector repository..." -ForegroundColor Yellow
    git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git .

    # Set up Visual Studio environment
    $vcvarsallPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"
    Write-Host "Setting up Visual Studio environment..." -ForegroundColor Yellow
    Write-Host "Using vcvarsall.bat from: $vcvarsallPath"

    if (-not (Test-Path $vcvarsallPath)) {
        throw "vcvarsall.bat not found at: $vcvarsallPath"
    }

    # Get Clang paths
    $clangPath = Join-Path $vsPath "VC\Tools\Llvm\x64\bin"
    $clangCl = Join-Path $clangPath "clang-cl.exe"
    $lldLink = Join-Path $clangPath "lld-link.exe"

    Write-Host "Using clang-cl from: $clangCl"
    Write-Host "Using lld-link from: $lldLink"

    if (-not (Test-Path $clangCl) -or -not (Test-Path $lldLink)) {
        throw "Clang tools not found. Please make sure Clang is installed with Visual Studio."
    }

    # Copy SQL files
    Copy-Item "sql\vector.sql" "sql\vector--0.6.0.sql"

    # Set up compilation flags
    $PG_CPPFLAGS = "/I`"$($env:PGINCLUDE)\server\port\win32_msvc`" /I`"$($env:PGINCLUDE)\server\port\win32`" /I`"$($env:PGINCLUDE)\server`" /I`"$($env:PGINCLUDE)`" /D_CRT_SECURE_NO_WARNINGS"
    $PG_CFLAGS = "/nologo /O2 /MT /Zi"

    # Initialize Visual Studio environment
    $initScript = "init_vs_env.bat"
@"
@echo off
call "$vcvarsallPath" x64
set > vs_env.txt
"@ | Out-File -FilePath $initScript -Encoding ASCII
    cmd /c $initScript
    Get-Content vs_env.txt | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }

    # Find all source files
    $sourceFiles = Get-ChildItem -Path "src" -Filter "*.c" -Recurse | Select-Object -ExpandProperty FullName
    $objectFiles = @()

    foreach ($sourceFile in $sourceFiles) {
        $objFile = [System.IO.Path]::ChangeExtension($sourceFile, ".obj")
        $objectFiles += $objFile
        
        $compileCmd = "& `"$clangCl`" $PG_CPPFLAGS $PG_CFLAGS /c `"$sourceFile`" /Fo`"$objFile`""
        Write-Host "Compiling $sourceFile..."
        Invoke-Expression $compileCmd
        if ($LASTEXITCODE -ne 0) {
            throw "Compilation failed for $sourceFile"
        }
    }

    # Link DLL
    $objFileList = $objectFiles -join " "
    $linkCmd = "& `"$lldLink`" /DLL /nologo /DEBUG /out:vector.dll $objFileList /LIBPATH:`"$($env:PGLIB)`" postgres.lib kernel32.lib user32.lib wsock32.lib ws2_32.lib secur32.lib ucrtd.lib msvcrtd.lib oldnames.lib"
    Write-Host "Linking vector.dll..."
    Invoke-Expression $linkCmd
    if ($LASTEXITCODE -ne 0) {
        throw "Linking failed"
    }

    # Check if the build was successful
    if (-not (Test-Path "vector.dll")) {
        throw "Build failed: vector.dll not found"
    }

    # Install the extension
    Write-Host "Installing pgvector extension..." -ForegroundColor Yellow
    Copy-Item "vector.dll" "$($env:PGLIB)" -Force
    Copy-Item "sql\vector--0.6.0.sql" "$($env:PGROOT)\share\extension" -Force
    Copy-Item "vector.control" "$($env:PGROOT)\share\extension" -Force

    # Restart PostgreSQL service
    Write-Host "Restarting PostgreSQL service..." -ForegroundColor Yellow
    Restart-Service -Name "postgresql-x64-16" -Force

    # Create extension in database
    Write-Host "Creating extension in database..." -ForegroundColor Yellow
    & psql -U postgres -d rag_doc_analyzer -c "CREATE EXTENSION IF NOT EXISTS vector;"

    Write-Host "pgvector installation completed!" -ForegroundColor Green
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
finally {
    Pop-Location
}
