# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Copying pgvector files..." -ForegroundColor Green

# Define paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_SHARE = "$PG_HOME\share"
$PG_LIB = "$PG_HOME\lib"
$PG_EXTENSION = "$PG_SHARE\extension"
$ZIP_PATH = "C:\Program Files\PostgreSQL\pgvector-master.zip"
$TEMP_DIR = ".\temp\pgvector_files"

# Create temp directory
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null
Set-Location $TEMP_DIR

try {
    # Extract zip
    Write-Host "Extracting pgvector source..." -ForegroundColor Yellow
    Expand-Archive -Path $ZIP_PATH -DestinationPath "." -Force

    Set-Location "pgvector-master"

    # Create necessary directories
    New-Item -ItemType Directory -Force -Path $PG_EXTENSION | Out-Null

    # Copy SQL file
    Write-Host "Copying SQL file..." -ForegroundColor Yellow
    $sqlFile = Get-ChildItem -Path "sql" -Filter "vector--*.sql" | Select-Object -First 1
    if ($sqlFile) {
        Copy-Item -Path $sqlFile.FullName -Destination "$PG_EXTENSION\vector--0.6.0.sql" -Force -Verbose
        Write-Host "SQL file copied successfully" -ForegroundColor Green
    } else {
        Write-Host "SQL file not found!" -ForegroundColor Red
    }

    # Copy control file
    Write-Host "Copying control file..." -ForegroundColor Yellow
    if (Test-Path "vector.control") {
        Copy-Item -Path "vector.control" -Destination "$PG_EXTENSION" -Force -Verbose
        Write-Host "Control file copied successfully" -ForegroundColor Green
    } else {
        Write-Host "Control file not found!" -ForegroundColor Red
    }

    # Verify files
    Write-Host "`nVerifying files:" -ForegroundColor Yellow
    Get-ChildItem -Path $PG_EXTENSION -Filter "vector*" | ForEach-Object {
        Write-Host "Found: $($_.FullName)" -ForegroundColor Green
    }

    # Show SQL file content
    Write-Host "`nSQL file content:" -ForegroundColor Yellow
    if (Test-Path "$PG_EXTENSION\vector--0.6.0.sql") {
        Get-Content "$PG_EXTENSION\vector--0.6.0.sql" | Select-Object -First 10
    }

    # Show control file content
    Write-Host "`nControl file content:" -ForegroundColor Yellow
    if (Test-Path "$PG_EXTENSION\vector.control") {
        Get-Content "$PG_EXTENSION\vector.control"
    }

} catch {
    Write-Error "An error occurred: $_"
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    throw
} finally {
    # Clean up
    Set-Location ..\..
    Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
}
