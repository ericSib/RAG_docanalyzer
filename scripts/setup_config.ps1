# Configuration par défaut
$DEFAULT_CONFIG = @{
    PG_VERSION = "16"
    PGVECTOR_VERSION = "0.6.0"
    INSTALL_METHOD = "msvc"
    WORKING_DIR = "C:\temp\pgvector_installation"
    PG_HOME = "C:\Program Files\PostgreSQL\16"
    PG_USER = "postgres"
    PG_PASSWORD = "admin123"
    MSVC_REQUIRED = $true
    CLEAN_AFTER_INSTALL = $true
}

# Fonction pour valider et compléter la configuration
function Initialize-Configuration {
    param (
        [Parameter(Mandatory=$false)]
        [hashtable]$UserConfig = @{}
    )

    # Fusionner la config utilisateur avec les valeurs par défaut
    $config = $DEFAULT_CONFIG.Clone()
    foreach ($key in $UserConfig.Keys) {
        $config[$key] = $UserConfig[$key]
    }

    # Dériver les chemins supplémentaires
    $config["PG_BIN"] = Join-Path $config["PG_HOME"] "bin"
    $config["PG_LIB"] = Join-Path $config["PG_HOME"] "lib"
    $config["PG_SHARE"] = Join-Path $config["PG_HOME"] "share"
    $config["PG_EXTENSION"] = Join-Path $config["PG_SHARE"] "extension"
    
    # Valider la configuration
    Validate-Configuration $config

    return $config
}

# Fonction pour valider la configuration
function Validate-Configuration {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )

    # Vérifier PostgreSQL
    if (-not (Test-Path $Config["PG_HOME"])) {
        throw "PostgreSQL installation not found at: $($Config['PG_HOME'])"
    }

    if (-not (Test-Path $Config["PG_BIN"])) {
        throw "PostgreSQL bin directory not found at: $($Config['PG_BIN'])"
    }

    # Vérifier la version de PostgreSQL
    $pgVersion = & "$($Config['PG_BIN'])\psql.exe" -V
    if (-not $pgVersion) {
        throw "Could not determine PostgreSQL version"
    }
    Write-Host "Found PostgreSQL: $pgVersion" -ForegroundColor Green

    # Vérifier Visual Studio si nécessaire
    if ($Config["INSTALL_METHOD"] -eq "msvc" -and $Config["MSVC_REQUIRED"]) {
        $vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
        if (-not $vsPath) {
            throw "Visual Studio installation not found (required for MSVC build method)"
        }
        Write-Host "Found Visual Studio at: $vsPath" -ForegroundColor Green
    }

    # Vérifier/créer le répertoire de travail
    if (-not (Test-Path $Config["WORKING_DIR"])) {
        try {
            New-Item -ItemType Directory -Force -Path $Config["WORKING_DIR"] | Out-Null
            Write-Host "Created working directory: $($Config['WORKING_DIR'])" -ForegroundColor Green
        }
        catch {
            throw "Failed to create working directory: $($Config['WORKING_DIR'])"
        }
    }

    # Vérifier les permissions d'écriture
    try {
        $testFile = Join-Path $Config["WORKING_DIR"] "test.txt"
        [System.IO.File]::WriteAllText($testFile, "test")
        Remove-Item $testFile -Force
        Write-Host "Write permissions verified on working directory" -ForegroundColor Green
    }
    catch {
        throw "No write permissions on working directory: $($Config['WORKING_DIR'])"
    }
}

# Fonction pour afficher la configuration
function Show-Configuration {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config
    )

    Write-Host "`nCurrent Configuration:" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    
    foreach ($key in $Config.Keys | Sort-Object) {
        $value = $Config[$key]
        Write-Host "${key}: " -NoNewline -ForegroundColor Yellow
        Write-Host "$value"
    }
    Write-Host "=====================`n" -ForegroundColor Cyan
}

# Fonction pour sauvegarder la configuration
function Save-Configuration {
    param (
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$false)]
        [string]$Path = ".\config\pgvector_config.json"
    )

    $configDir = Split-Path $Path -Parent
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    }

    $Config | ConvertTo-Json -Depth 10 | Set-Content $Path
    Write-Host "Configuration saved to: $Path" -ForegroundColor Green
}

# Fonction pour charger la configuration
function Load-Configuration {
    param (
        [Parameter(Mandatory=$false)]
        [string]$Path = ".\config\pgvector_config.json"
    )

    if (-not (Test-Path $Path)) {
        throw "Configuration file not found: $Path"
    }

    $loadedConfig = Get-Content $Path | ConvertFrom-Json
    $config = @{}
    
    # Convertir l'objet JSON en hashtable
    $loadedConfig.PSObject.Properties | ForEach-Object {
        $config[$_.Name] = $_.Value
    }

    return Initialize-Configuration $config
}

# Exemple d'utilisation
$config = Initialize-Configuration @{
    PG_VERSION = "16"
    PGVECTOR_VERSION = "0.6.0"
    INSTALL_METHOD = "msvc"
    WORKING_DIR = "C:\temp\pgvector_installation"
}

Show-Configuration $config
Save-Configuration $config

# Exporter les fonctions et la configuration
Export-ModuleMember -Function Initialize-Configuration, Validate-Configuration, Show-Configuration, Save-Configuration, Load-Configuration
Export-ModuleMember -Variable DEFAULT_CONFIG
