cd c:\DEV\RAG_Doc-analyzer
Set-ExecutionPolicy Bypass -Scope Process -Force
.\scripts\install_pgvector_msvc.ps1# Requires -RunAsAdministrator

Write-Host "Installing pgvector dependencies..." -ForegroundColor Green

# Clone vcpkg if not exists
if (-not (Test-Path "C:\vcpkg")) {
    Write-Host "Cloning vcpkg..." -ForegroundColor Yellow
    git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
    C:\vcpkg\bootstrap-vcpkg.bat
}

# Add vcpkg to PATH
$env:Path = "C:\vcpkg;" + $env:Path

# Install pgvector
Write-Host "Installing pgvector..." -ForegroundColor Yellow
C:\vcpkg\vcpkg install pgvector:x64-windows

Write-Host "Installation completed." -ForegroundColor Green
Write-Host "Please restart PostgreSQL service to apply changes." -ForegroundColor Yellow

# Restart PostgreSQL service
$serviceName = "postgresql-x64-17"
Write-Host "Restarting PostgreSQL service..." -ForegroundColor Yellow
Stop-Service -Name $serviceName -Force
Start-Service -Name $serviceName

Write-Host "PostgreSQL service restarted successfully." -ForegroundColor Green

# Verify pgvector installation
$pgPass = "admin123"
$env:PGPASSWORD = $pgPass

Write-Host "Verifying pgvector installation..." -ForegroundColor Yellow
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

Write-Host "Setup completed. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
