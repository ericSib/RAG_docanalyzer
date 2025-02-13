# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Installing pgvector from binary..." -ForegroundColor Green

# Define paths
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_SHARE = "$PG_HOME\share"
$PG_LIB = "$PG_HOME\lib"
$PG_EXTENSION = "$PG_SHARE\extension"
$TEMP_DIR = ".\temp\pgvector_binary"

# Create temp directory
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null
Set-Location $TEMP_DIR

try {
    # Download pgvector Windows binaries
    Write-Host "Downloading pgvector binaries..." -ForegroundColor Yellow
    $url = "https://github.com/pgvector/pgvector/releases/download/v0.5.1/vector-0.5.1-pg16-windows-x64.zip"
    $output = "pgvector.zip"
    
    Invoke-WebRequest -Uri $url -OutFile $output
    Expand-Archive -Path $output -DestinationPath "." -Force

    # Copy files
    Write-Host "Installing files..." -ForegroundColor Yellow
    
    Write-Host "Copying vector.dll to $PG_LIB..." -ForegroundColor Yellow
    Copy-Item -Path "bin\vector.dll" -Destination "$PG_LIB" -Force -Verbose
    
    Write-Host "Copying SQL file to $PG_EXTENSION..." -ForegroundColor Yellow
    Copy-Item -Path "share\extension\vector--0.5.1.sql" -Destination "$PG_EXTENSION" -Force -Verbose
    
    Write-Host "Copying control file to $PG_EXTENSION..." -ForegroundColor Yellow
    Copy-Item -Path "share\extension\vector.control" -Destination "$PG_EXTENSION" -Force -Verbose

    # Verify files
    Write-Host "`nVerifying installed files:" -ForegroundColor Yellow
    if (Test-Path "$PG_LIB\vector.dll") {
        Write-Host "vector.dll is present" -ForegroundColor Green
    } else {
        Write-Host "vector.dll is missing!" -ForegroundColor Red
    }

    if (Test-Path "$PG_EXTENSION\vector--0.5.1.sql") {
        Write-Host "vector--0.5.1.sql is present" -ForegroundColor Green
    } else {
        Write-Host "vector--0.5.1.sql is missing!" -ForegroundColor Red
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
    throw
} finally {
    # Clean up
    Set-Location ..
    Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
}
