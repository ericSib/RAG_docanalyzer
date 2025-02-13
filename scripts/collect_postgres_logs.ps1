# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

# Create log output directory
$outputDir = ".\postgres_logs"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

# Start transcript
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$transcriptFile = Join-Path $outputDir "log_collection_$timestamp.txt"
Start-Transcript -Path $transcriptFile

Write-Host "PostgreSQL Log Collection Tool" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Configuration
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"

# 1. Collect Windows Event Logs
Write-Host "`nCollecting Windows Event Logs..." -ForegroundColor Yellow
$eventLogFile = Join-Path $outputDir "postgres_event_log.txt"
Get-EventLog -LogName Application -Source "PostgreSQL" -Newest 50 | 
    Format-Table TimeGenerated, EntryType, Message -AutoSize -Wrap | 
    Out-File $eventLogFile
Write-Host "Event logs saved to: $eventLogFile"

# 2. Check PostgreSQL log directories
$logDirs = @(
    "$PG_DATA\log",
    "$PG_DATA\pg_log",
    "$PG_DATA\logs",
    "$PG_HOME\logs"
)

Write-Host "`nChecking PostgreSQL log directories..." -ForegroundColor Yellow
foreach ($dir in $logDirs) {
    if (Test-Path $dir) {
        Write-Host "Found log directory: $dir"
        Get-ChildItem $dir -Filter *.log | ForEach-Object {
            $destFile = Join-Path $outputDir $_.Name
            Copy-Item $_.FullName $destFile
            Write-Host "Copied log file: $($_.Name)"
        }
    }
}

# 3. Check postgresql.conf for log settings
Write-Host "`nChecking postgresql.conf for log settings..." -ForegroundColor Yellow
$confFile = "$PG_DATA\postgresql.conf"
if (Test-Path $confFile) {
    $logSettings = Get-Content $confFile | Where-Object { 
        $_ -match "^[^#].*log.*=" -or 
        $_ -match "^[^#].*syslog.*=" -or 
        $_ -match "^[^#].*debug.*="
    }
    $logSettingsFile = Join-Path $outputDir "log_settings.txt"
    $logSettings | Out-File $logSettingsFile
    Write-Host "Log settings saved to: $logSettingsFile"
}

# 4. Check service status and configuration
Write-Host "`nChecking PostgreSQL service..." -ForegroundColor Yellow
$serviceInfo = Join-Path $outputDir "service_info.txt"
$service = Get-Service "postgresql*" -ErrorAction SilentlyContinue
if ($service) {
    "Service Name: $($service.Name)" | Out-File $serviceInfo
    "Display Name: $($service.DisplayName)" | Out-File $serviceInfo -Append
    "Status: $($service.Status)" | Out-File $serviceInfo -Append
    "Start Type: $($service.StartType)" | Out-File $serviceInfo -Append
    
    # Get service binary path
    $regKey = "HKLM:\SYSTEM\CurrentControlSet\Services\$($service.Name)"
    if (Test-Path $regKey) {
        $imagePath = (Get-ItemProperty -Path $regKey).ImagePath
        "Binary Path: $imagePath" | Out-File $serviceInfo -Append
    }
}
Write-Host "Service information saved to: $serviceInfo"

# 5. Test PostgreSQL connection and get status
Write-Host "`nTesting PostgreSQL connection..." -ForegroundColor Yellow
$connectionTest = Join-Path $outputDir "connection_test.txt"
$env:PGPASSWORD = "admin123"
try {
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "\conninfo" 2>&1 | Out-File $connectionTest
    & "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();" 2>&1 | Out-File $connectionTest -Append
} catch {
    "Connection test failed: $_" | Out-File $connectionTest
}
Write-Host "Connection test results saved to: $connectionTest"

Write-Host "`nLog collection complete!" -ForegroundColor Green
Write-Host "All logs have been saved to: $outputDir" -ForegroundColor Green

Stop-Transcript
