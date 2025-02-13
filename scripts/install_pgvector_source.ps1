# Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "Installing pgvector from source..." -ForegroundColor Green

# Create temp directory
$tempDir = "C:\temp\pgvector_build"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

# Clone pgvector repository
Write-Host "Cloning pgvector repository..." -ForegroundColor Yellow
git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git .

# Set up build environment
Write-Host "Setting up build environment..." -ForegroundColor Yellow
$PG_HOME = "C:\Program Files\PostgreSQL\17"
$MINGW_HOME = "C:\ProgramData\chocolatey\lib\mingw\tools\install\mingw64"
$env:PATH = "$MINGW_HOME\bin;$PG_HOME\bin;$env:PATH"
$env:PG_CONFIG = "$PG_HOME\bin\pg_config"

# Build pgvector
Write-Host "Building pgvector..." -ForegroundColor Yellow
Write-Host "Current PATH: $env:PATH" -ForegroundColor Gray

# Run make commands using mingw32-make
$makeCmd = "mingw32-make"
Write-Host "Running $makeCmd..." -ForegroundColor Yellow
& $makeCmd
if ($LASTEXITCODE -ne 0) {
    throw "Make failed with exit code $LASTEXITCODE"
}

Write-Host "Running $makeCmd install..." -ForegroundColor Yellow
& $makeCmd install
if ($LASTEXITCODE -ne 0) {
    throw "Make install failed with exit code $LASTEXITCODE"
}

Write-Host "Installation completed." -ForegroundColor Green
Write-Host "Restarting PostgreSQL service..." -ForegroundColor Yellow

# Restart PostgreSQL service
$serviceName = "postgresql-x64-17"
Stop-Service -Name $serviceName -Force
Start-Service -Name $serviceName

Write-Host "PostgreSQL service restarted successfully." -ForegroundColor Green

# Clean up
Set-Location C:\
Remove-Item -Recurse -Force $tempDir

# Verify installation
$pgPass = "admin123"
$env:PGPASSWORD = $pgPass

Write-Host "Verifying pgvector installation..." -ForegroundColor Yellow
& "$PG_HOME\bin\psql.exe" -U postgres -h localhost -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

Write-Host "Setup completed. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
