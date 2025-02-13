# Importer la configuration
. "$PSScriptRoot\setup_config.ps1"

# Fonction pour vérifier les prérequis
function Test-Prerequisites {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )
    
    Write-Host "Checking prerequisites..." -ForegroundColor Cyan
    
    # Vérifier PostgreSQL
    try {
        $pgVersion = & "$($Config.PG_BIN)\psql.exe" -V
        if ($pgVersion -notmatch $Config.PG_VERSION) {
            throw "PostgreSQL version mismatch. Expected $($Config.PG_VERSION), found: $pgVersion"
        }
        Write-Host "✓ PostgreSQL $($Config.PG_VERSION) found" -ForegroundColor Green
    }
    catch {
        throw "PostgreSQL check failed: $_"
    }

    # Vérifier Visual Studio si nécessaire
    if ($Config.INSTALL_METHOD -eq "msvc") {
        try {
            $vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
            $vcvarsallPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"
            if (-not (Test-Path $vcvarsallPath)) {
                throw "Visual Studio C++ build tools not found"
            }
            Write-Host "✓ Visual Studio build tools found" -ForegroundColor Green
            return $vcvarsallPath
        }
        catch {
            throw "Visual Studio check failed: $_"
        }
    }
}

# Fonction pour sauvegarder les fichiers existants
function Backup-ExistingFiles {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )
    
    Write-Host "Backing up existing files..." -ForegroundColor Cyan
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $Config.WORKING_DIR "backup_$timestamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

    $filesToBackup = @(
        (Join-Path $Config.PG_LIB "vector.dll"),
        (Join-Path $Config.PG_EXTENSION "vector.control"),
        (Join-Path $Config.PG_EXTENSION "vector--*.sql")
    )

    foreach ($file in $filesToBackup) {
        if (Test-Path $file) {
            $destPath = Join-Path $backupDir (Split-Path $file -Leaf)
            Copy-Item -Path $file -Destination $destPath -Force
            Write-Host "✓ Backed up: $file" -ForegroundColor Green
        }
    }

    return $backupDir
}

# Fonction pour installer via MSVC
function Install-PgVectorMSVC {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [string]$VcVarsallPath
    )
    
    Write-Host "Installing pgvector using MSVC..." -ForegroundColor Cyan
    
    Push-Location $Config.WORKING_DIR
    try {
        # Cloner le dépôt
        git clone --branch "v$($Config.PGVECTOR_VERSION)" https://github.com/pgvector/pgvector.git .
        
        # Créer le Makefile
        $makefileContent = @"
EXTENSION = vector
MODULE_big = vector
OBJS = src/hnsw.o src/hnswbuild.o src/hnswinsert.o src/hnswscan.o src/hnswutils.o src/hnswvacuum.o src/ivfbuild.o src/ivfflat.o src/ivfinsert.o src/ivfkmeans.o src/ivfscan.o src/ivfutils.o src/ivfvacuum.o src/vector.o
DATA = sql/vector--$($Config.PGVECTOR_VERSION).sql

PG_CONFIG = "$($Config.PG_BIN)\pg_config.exe"
PGFILEDESC = "pgvector - vector data type and ivfflat and hnsw access methods"

USE_PGXS = 1

PG_CPPFLAGS = /I"$(& "$($Config.PG_BIN)\pg_config.exe" --includedir-server)"
SHLIB_LINK = /LIBPATH:"$(& "$($Config.PG_BIN)\pg_config.exe" --libdir)"

include $(shell "$($Config.PG_BIN)\pg_config.exe" --pgxs)
"@
        $makefileContent | Out-File -FilePath "Makefile.win" -Encoding ASCII

        # Créer le script de build
        $buildScript = @"
@echo off
call "$VcVarsallPath" x64
nmake /f Makefile.win
if errorlevel 1 exit /b 1
"@
        $buildScript | Out-File -FilePath "build.bat" -Encoding ASCII

        # Compiler
        $buildProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "build.bat" -NoNewWindow -PassThru -Wait
        if ($buildProcess.ExitCode -ne 0) {
            throw "Build failed with exit code: $($buildProcess.ExitCode)"
        }

        Write-Host "✓ Compilation successful" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "MSVC installation failed: $_"
        return $false
    }
    finally {
        Pop-Location
    }
}

# Fonction pour installer via binaires précompilés
function Install-PgVectorBinary {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )
    
    Write-Host "Installing pgvector using pre-compiled binaries..." -ForegroundColor Cyan
    
    Push-Location $Config.WORKING_DIR
    try {
        $url = "https://github.com/pgvector/pgvector/releases/download/v$($Config.PGVECTOR_VERSION)/vector-$($Config.PGVECTOR_VERSION)-pg$($Config.PG_VERSION)-windows-x64.zip"
        $output = "pgvector.zip"
        
        Invoke-WebRequest -Uri $url -OutFile $output
        Expand-Archive -Path $output -DestinationPath "." -Force
        
        Write-Host "✓ Downloaded and extracted binaries" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Binary installation failed: $_"
        return $false
    }
    finally {
        Pop-Location
    }
}

# Fonction pour installer les fichiers
function Install-Files {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )
    
    Write-Host "Installing files..." -ForegroundColor Cyan
    
    try {
        # Copier les fichiers
        Copy-Item -Path (Join-Path $Config.WORKING_DIR "vector.dll") -Destination $Config.PG_LIB -Force
        Copy-Item -Path (Join-Path $Config.WORKING_DIR "sql\vector--$($Config.PGVECTOR_VERSION).sql") -Destination $Config.PG_EXTENSION -Force
        Copy-Item -Path (Join-Path $Config.WORKING_DIR "vector.control") -Destination $Config.PG_EXTENSION -Force
        
        Write-Host "✓ Files installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "File installation failed: $_"
        return $false
    }
}

# Fonction pour créer l'extension dans la base de données
function Install-DatabaseExtension {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )
    
    Write-Host "Creating database extension..." -ForegroundColor Cyan
    
    try {
        $env:PGPASSWORD = $Config.PG_PASSWORD
        
        # Supprimer l'ancienne extension si elle existe
        & "$($Config.PG_BIN)\psql.exe" -U $Config.PG_USER -d postgres -c "DROP EXTENSION IF EXISTS vector;"
        
        # Créer la nouvelle extension
        & "$($Config.PG_BIN)\psql.exe" -U $Config.PG_USER -d postgres -c "CREATE EXTENSION vector;"
        
        # Vérifier l'installation
        $result = & "$($Config.PG_BIN)\psql.exe" -U $Config.PG_USER -d postgres -c "\dx vector"
        if ($result -match "vector") {
            Write-Host "✓ Database extension created successfully" -ForegroundColor Green
            return $true
        }
        
        throw "Extension not found after installation"
    }
    catch {
        Write-Error "Database extension installation failed: $_"
        return $false
    }
}

# Fonction pour restaurer la sauvegarde en cas d'échec
function Restore-Backup {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [string]$BackupDir
    )
    
    Write-Host "Restoring from backup..." -ForegroundColor Yellow
    
    try {
        Get-ChildItem -Path $BackupDir | ForEach-Object {
            if ($_.Name -like "vector.dll") {
                Copy-Item -Path $_.FullName -Destination $Config.PG_LIB -Force
            }
            else {
                Copy-Item -Path $_.FullName -Destination $Config.PG_EXTENSION -Force
            }
        }
        
        Write-Host "✓ Backup restored successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Backup restoration failed: $_"
        return $false
    }
}

# Fonction principale d'installation
function Install-PgVector {
    param (
        [Parameter(Mandatory=$false)]
        [hashtable]$UserConfig = @{}
    )
    
    $config = Initialize-Configuration $UserConfig
    Show-Configuration $config
    
    try {
        # Étape 1: Vérifier les prérequis
        $vcvarsallPath = Test-Prerequisites $config
        
        # Étape 2: Sauvegarder les fichiers existants
        $backupDir = Backup-ExistingFiles $config
        
        # Étape 3: Installation selon la méthode choisie
        $installSuccess = switch ($config.INSTALL_METHOD) {
            "msvc" { Install-PgVectorMSVC $config $vcvarsallPath }
            "binary" { Install-PgVectorBinary $config }
            default { throw "Unsupported installation method: $($config.INSTALL_METHOD)" }
        }
        
        if (-not $installSuccess) {
            throw "Installation failed"
        }
        
        # Étape 4: Installer les fichiers
        $filesSuccess = Install-Files $config
        if (-not $filesSuccess) {
            throw "File installation failed"
        }
        
        # Étape 5: Créer l'extension dans la base de données
        $dbSuccess = Install-DatabaseExtension $config
        if (-not $dbSuccess) {
            throw "Database extension installation failed"
        }
        
        Write-Host "`nPgVector installation completed successfully!" -ForegroundColor Green
        
    }
    catch {
        Write-Error "Installation failed: $_"
        
        # Restaurer la sauvegarde
        if ($backupDir) {
            Restore-Backup $config $backupDir
        }
        
        throw
    }
    finally {
        # Nettoyage
        if ($config.CLEAN_AFTER_INSTALL -and (Test-Path $config.WORKING_DIR)) {
            Remove-Item -Recurse -Force $config.WORKING_DIR -ErrorAction SilentlyContinue
        }
    }
}

# Exemple d'utilisation
try {
    Install-PgVector @{
        PG_VERSION = "16"
        PGVECTOR_VERSION = "0.6.0"
        INSTALL_METHOD = "msvc"
    }
}
catch {
    Write-Error "Installation failed: $_"
    exit 1
}
