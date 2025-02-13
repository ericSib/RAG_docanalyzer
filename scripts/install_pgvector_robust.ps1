# Module d'installation robuste pour pgvector
using namespace System.IO

# Configuration par défaut
$Script:Config = @{
    PostgresVersion = "16"
    PgVectorVersion = "0.6.0"
    PostgresPath = "C:\Program Files\PostgreSQL\16"
    WorkingDir = "C:\temp\pgvector_install"
    PostgresUser = "postgres"
    PostgresPassword = "admin123"
}

# Enumération des méthodes d'installation
enum InstallMethod {
    MSVC
    Binary
    Source
}

# Classes pour la gestion des erreurs
class InstallationError : Exception {
    [string] $Component
    [string] $Details
    
    InstallationError([string]$component, [string]$message) : base($message) {
        $this.Component = $component
        $this.Details = $message
    }
}

# Fonction de logging
function Write-InstallLog {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('Info', 'Warning', 'Error', 'Success')]
        [string]$Level = 'Info'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch($Level) {
        'Info' { 'White' }
        'Warning' { 'Yellow' }
        'Error' { 'Red' }
        'Success' { 'Green' }
    }
    
    Write-Host "[$timestamp] $Level : $Message" -ForegroundColor $color
    
    # Log to file
    $logPath = Join-Path $Script:Config.WorkingDir "install.log"
    "[$timestamp] $Level : $Message" | Add-Content -Path $logPath
}

function Test-Prerequisites {
    [CmdletBinding()]
    param()
    
    Write-InstallLog "Checking prerequisites..." -Level Info
    
    try {
        # 1. Vérifier PostgreSQL
        $pgVersion = & "$($Script:Config.PostgresPath)\bin\psql.exe" -V
        if (-not $pgVersion) {
            throw [InstallationError]::new('PostgreSQL', "PostgreSQL not found at $($Script:Config.PostgresPath)")
        }
        Write-InstallLog "PostgreSQL found: $pgVersion" -Level Success

        # 2. Vérifier Visual Studio
        $vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
        if (-not $vsPath) {
            throw [InstallationError]::new('VisualStudio', "Visual Studio not found")
        }
        
        $vcvarsallPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"
        if (-not (Test-Path $vcvarsallPath)) {
            throw [InstallationError]::new('VisualStudio', "Visual C++ build tools not found")
        }
        Write-InstallLog "Visual Studio found at: $vsPath" -Level Success

        # 3. Vérifier Git
        $git = Get-Command git -ErrorAction SilentlyContinue
        if (-not $git) {
            throw [InstallationError]::new('Git', "Git not found")
        }
        Write-InstallLog "Git found: $($git.Version)" -Level Success

        # 4. Vérifier les permissions
        $testFile = Join-Path $Script:Config.WorkingDir "test.txt"
        try {
            [System.IO.File]::WriteAllText($testFile, "test")
            Remove-Item $testFile -Force
            Write-InstallLog "Write permissions verified" -Level Success
        }
        catch {
            throw [InstallationError]::new('Permissions', "No write permissions in working directory")
        }

        # 5. Vérifier l'espace disque
        $drive = Split-Path $Script:Config.WorkingDir -Qualifier
        $freeSpace = (Get-PSDrive $drive.TrimEnd(':')).Free
        if ($freeSpace -lt 1GB) {
            throw [InstallationError]::new('DiskSpace', "Insufficient disk space")
        }
        Write-InstallLog "Sufficient disk space available" -Level Success

        return @{
            Success = $true
            VcVarsallPath = $vcvarsallPath
        }
    }
    catch [InstallationError] {
        Write-InstallLog "Prerequisite check failed: $($_.Exception.Message)" -Level Error
        throw
    }
    catch {
        Write-InstallLog "Unexpected error during prerequisite check: $_" -Level Error
        throw [InstallationError]::new('Unknown', $_.Exception.Message)
    }
}

function Install-Pgvector {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [InstallMethod]$Method,
        
        [Parameter(Mandatory=$false)]
        [string]$Version = $Script:Config.PgVectorVersion
    )
    
    $backupDir = $null
    
    try {
        # 1. Préparation
        Write-InstallLog "Starting pgvector installation (Method: $Method, Version: $Version)" -Level Info
        
        # Vérifier les prérequis
        $prereqs = Test-Prerequisites
        
        # Créer le répertoire de travail
        if (-not (Test-Path $Script:Config.WorkingDir)) {
            New-Item -ItemType Directory -Force -Path $Script:Config.WorkingDir | Out-Null
        }
        
        # Backup des fichiers existants
        $backupDir = Backup-ExistingFiles
        
        # 2. Installation selon la méthode
        switch($Method) {
            'MSVC' { 
                Install-PgvectorMSVC -Version $Version -VcVarsallPath $prereqs.VcVarsallPath 
            }
            'Binary' { 
                Install-PgvectorBinary -Version $Version 
            }
            'Source' { 
                Install-PgvectorSource -Version $Version 
            }
        }
        
        # 3. Validation
        if (-not (Test-Installation)) {
            throw [InstallationError]::new('Validation', "Installation validation failed")
        }
        
        Write-InstallLog "Installation completed successfully" -Level Success
    }
    catch {
        Write-InstallLog "Installation failed: $_" -Level Error
        
        # Rollback
        if ($backupDir) {
            Write-InstallLog "Rolling back changes..." -Level Warning
            Restore-FromBackup -BackupDir $backupDir
        }
        
        throw
    }
    finally {
        # 4. Nettoyage
        if (Test-Path $Script:Config.WorkingDir) {
            Remove-Item -Recurse -Force $Script:Config.WorkingDir -ErrorAction SilentlyContinue
        }
    }
}

function Test-Installation {
    [CmdletBinding()]
    param()
    
    Write-InstallLog "Testing installation..." -Level Info
    
    try {
        # 1. Vérifier les fichiers
        $requiredFiles = @(
            (Join-Path $Script:Config.PostgresPath "lib\vector.dll"),
            (Join-Path $Script:Config.PostgresPath "share\extension\vector.control"),
            (Join-Path $Script:Config.PostgresPath "share\extension\vector--$($Script:Config.PgVectorVersion).sql")
        )
        
        foreach ($file in $requiredFiles) {
            if (-not (Test-Path $file)) {
                throw [InstallationError]::new('Files', "Required file missing: $file")
            }
        }
        
        # 2. Vérifier l'extension PostgreSQL
        $env:PGPASSWORD = $Script:Config.PostgresPassword
        $extensionCheck = & "$($Script:Config.PostgresPath)\bin\psql.exe" -U $Script:Config.PostgresUser -d postgres -t -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
        
        if (-not $extensionCheck) {
            throw [InstallationError]::new('Extension', "Vector extension not found in PostgreSQL")
        }
        
        # 3. Test fonctionnel
        $testQueries = @(
            "CREATE TABLE vector_test (id serial PRIMARY KEY, embedding vector(3));",
            "INSERT INTO vector_test (embedding) VALUES ('[1,2,3]');",
            "SELECT * FROM vector_test WHERE embedding <-> '[1,1,1]' < 2;"
        )
        
        foreach ($query in $testQueries) {
            $result = & "$($Script:Config.PostgresPath)\bin\psql.exe" -U $Script:Config.PostgresUser -d postgres -c $query
            if ($LASTEXITCODE -ne 0) {
                throw [InstallationError]::new('Functional', "Query failed: $query")
            }
        }
        
        # Nettoyage du test
        & "$($Script:Config.PostgresPath)\bin\psql.exe" -U $Script:Config.PostgresUser -d postgres -c "DROP TABLE vector_test;"
        
        Write-InstallLog "All tests passed successfully" -Level Success
        return $true
    }
    catch {
        Write-InstallLog "Installation test failed: $_" -Level Error
        return $false
    }
}

# Fonctions auxiliaires
function Backup-ExistingFiles {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $Script:Config.WorkingDir "backup_$timestamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    
    $filesToBackup = @(
        (Join-Path $Script:Config.PostgresPath "lib\vector.dll"),
        (Join-Path $Script:Config.PostgresPath "share\extension\vector.control"),
        (Join-Path $Script:Config.PostgresPath "share\extension\vector--*.sql")
    )
    
    foreach ($file in $filesToBackup) {
        if (Test-Path $file) {
            Copy-Item -Path $file -Destination $backupDir
        }
    }
    
    return $backupDir
}

function Restore-FromBackup {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BackupDir
    )
    
    if (Test-Path $BackupDir) {
        Get-ChildItem -Path $BackupDir | ForEach-Object {
            if ($_.Name -like "vector.dll") {
                Copy-Item -Path $_.FullName -Destination (Join-Path $Script:Config.PostgresPath "lib") -Force
            } else {
                Copy-Item -Path $_.FullName -Destination (Join-Path $Script:Config.PostgresPath "share\extension") -Force
            }
        }
    }
}

# Exemple d'utilisation
try {
    Install-Pgvector -Method MSVC -Version "0.6.0"
}
catch {
    Write-Error "Installation failed: $_"
    exit 1
}
