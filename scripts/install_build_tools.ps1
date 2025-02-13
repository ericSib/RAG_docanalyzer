# Requires -RunAsAdministrator

Write-Host "Installing build tools..." -ForegroundColor Green

# Install chocolatey if not already installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    
    # Reload PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Install required build tools
Write-Host "Installing MinGW and other build tools..." -ForegroundColor Yellow
choco install mingw --version=12.2.0.03042023 -y
choco install make -y

# Add MinGW to PATH if not already there
$mingwPath = "C:\ProgramData\chocolatey\lib\mingw\tools\install\mingw64\bin"
if ($env:Path -notlike "*$mingwPath*") {
    $env:Path = "$mingwPath;" + $env:Path
    [System.Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)
}

# Install PostgreSQL development files
Write-Host "Installing PostgreSQL development files..." -ForegroundColor Yellow
choco install postgresql17 --params '/Password:admin123' -y

Write-Host "Build tools installation completed." -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
