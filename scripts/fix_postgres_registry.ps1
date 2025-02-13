# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "Fixing PostgreSQL registry entries..." -ForegroundColor Green

# Stop PostgreSQL service
$serviceName = "postgresql-x64-16"
Write-Host "Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $serviceName -Force -ErrorAction SilentlyContinue

# Backup registry
Write-Host "Creating registry backup..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = ".\PostgreSQL_registry_backup_$timestamp.reg"
reg export "HKLM\SOFTWARE\PostgreSQL" $backupFile /y

# Update PostgreSQL registry entries
Write-Host "Updating registry entries..." -ForegroundColor Yellow
$registryPath = "HKLM:\SOFTWARE\PostgreSQL"

function Update-RegistryValues {
    param (
        [string]$path
    )
    
    if (Test-Path $path) {
        $properties = Get-ItemProperty -Path $path
        foreach ($prop in $properties.PSObject.Properties) {
            if ($prop.Name -notlike "PS*") {  # Skip PowerShell automatic properties
                $value = $prop.Value
                if ($value -is [string] -and $value -like "*PostgreSQL\17*") {
                    $newValue = $value -replace "PostgreSQL\\17", "PostgreSQL\16"
                    Write-Host "Updating $($prop.Name): $value -> $newValue"
                    Set-ItemProperty -Path $path -Name $prop.Name -Value $newValue
                }
            }
        }
        
        # Process subkeys recursively
        Get-ChildItem -Path $path -ErrorAction SilentlyContinue | ForEach-Object {
            Update-RegistryValues $_.PSPath
        }
    }
}

Update-RegistryValues $registryPath

# Update postgresql.conf
Write-Host "Updating postgresql.conf..." -ForegroundColor Yellow
$pg16Home = "C:\Program Files\PostgreSQL\16"
$pg16Data = "$pg16Home\data"
$postgresqlConf = "$pg16Data\postgresql.conf"

if (Test-Path $postgresqlConf) {
    $content = Get-Content $postgresqlConf -Raw
    $newContent = $content -replace "PostgreSQL/17", "PostgreSQL/16" -replace "PostgreSQL\\17", "PostgreSQL\16"
    Set-Content -Path $postgresqlConf -Value $newContent
    Write-Host "Updated postgresql.conf with correct paths"
}

# Start PostgreSQL service
Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $serviceName

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify configuration
Write-Host "`nVerifying configuration:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$pg16Home\bin\psql.exe" -U postgres -d postgres -c "SHOW config_file; SHOW data_directory;"

Write-Host "`nRegistry and configuration update complete!" -ForegroundColor Green
Write-Host "A backup of the registry has been saved to: $backupFile" -ForegroundColor Green
