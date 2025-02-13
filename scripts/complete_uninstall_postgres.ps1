# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Complete PostgreSQL uninstallation cleanup..." -ForegroundColor Green

# 1. Stop all PostgreSQL services
Write-Host "Stopping PostgreSQL services..." -ForegroundColor Yellow
Get-Service | Where-Object {$_.Name -like "postgresql*"} | ForEach-Object {
    Write-Host "Stopping service: $($_.Name)" -ForegroundColor Yellow
    Stop-Service $_.Name -Force -ErrorAction SilentlyContinue
    
    Write-Host "Removing service: $($_.Name)" -ForegroundColor Yellow
    & sc.exe delete $_.Name
}

# 2. Remove PostgreSQL directories
$dirsToRemove = @(
    "C:\Program Files\PostgreSQL",
    "C:\Program Files (x86)\PostgreSQL",
    "$env:ProgramData\PostgreSQL"
)

foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Write-Host "Removing directory: $dir" -ForegroundColor Yellow
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# 3. Clean Registry
Write-Host "Cleaning registry..." -ForegroundColor Yellow

# Backup registry first
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = ".\PostgreSQL_registry_backup_$timestamp.reg"
reg export "HKLM\SOFTWARE\PostgreSQL" $backupFile /y

$registryPaths = @(
    "HKLM:\SOFTWARE\PostgreSQL",
    "HKLM:\SOFTWARE\Wow6432Node\PostgreSQL"
)

foreach ($path in $registryPaths) {
    if (Test-Path $path) {
        Write-Host "Removing registry key: $path" -ForegroundColor Yellow
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Remove service entries
$servicePaths = Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services" -ErrorAction SilentlyContinue | 
    Where-Object { $_.PSChildName -like "postgresql*" }

foreach ($service in $servicePaths) {
    Write-Host "Removing service registry key: $($service.PSPath)" -ForegroundColor Yellow
    Remove-Item -Path $service.PSPath -Recurse -Force -ErrorAction SilentlyContinue
}

# 4. Remove environment variables
Write-Host "Removing PostgreSQL environment variables..." -ForegroundColor Yellow
$envVars = [System.Environment]::GetEnvironmentVariables([System.EnvironmentVariableTarget]::Machine)
foreach ($var in $envVars.Keys) {
    if ($var -like "*POSTGRES*" -or $var -like "*PG*") {
        [System.Environment]::SetEnvironmentVariable($var, $null, [System.EnvironmentVariableTarget]::Machine)
        Write-Host "Removed environment variable: $var" -ForegroundColor Yellow
    }
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host "A backup of the registry has been saved to: $backupFile" -ForegroundColor Green
Write-Host "`nPlease follow these steps:" -ForegroundColor Yellow
Write-Host "1. Restart your computer" -ForegroundColor Yellow
Write-Host "2. Download PostgreSQL 16 installer from the official website" -ForegroundColor Yellow
Write-Host "3. Run the installer and choose C:\Program Files\PostgreSQL\16 as the installation directory" -ForegroundColor Yellow
Write-Host "4. After installation, we'll configure pgvector" -ForegroundColor Yellow
