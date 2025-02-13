# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "PostgreSQL Diagnostic Tool" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

# Configuration
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# 1. Check directories
Write-Host "`nChecking directories:" -ForegroundColor Yellow
@(
    $PG_HOME,
    $PG_DATA,
    "$PG_HOME\bin",
    "$PG_HOME\lib",
    "$PG_HOME\share"
) | ForEach-Object {
    Write-Host "Directory $($_): " -NoNewline
    if (Test-Path $_) {
        Write-Host "EXISTS" -ForegroundColor Green
    } else {
        Write-Host "MISSING" -ForegroundColor Red
    }
}

# 2. Check critical files
Write-Host "`nChecking critical files:" -ForegroundColor Yellow
@(
    "$PG_HOME\bin\postgres.exe",
    "$PG_HOME\bin\pg_ctl.exe",
    "$PG_DATA\postgresql.conf",
    "$PG_DATA\pg_hba.conf"
) | ForEach-Object {
    Write-Host "File $($_): " -NoNewline
    if (Test-Path $_) {
        Write-Host "EXISTS" -ForegroundColor Green
    } else {
        Write-Host "MISSING" -ForegroundColor Red
    }
}

# 3. Check service
Write-Host "`nChecking service:" -ForegroundColor Yellow
$service = Get-Service $SERVICE_NAME -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "Service Name: $($service.Name)"
    Write-Host "Display Name: $($service.DisplayName)"
    Write-Host "Status: $($service.Status)"
    Write-Host "Start Type: $($service.StartType)"
    
    # Get service binary path
    $serviceInfo = & sc.exe qc $SERVICE_NAME
    Write-Host "Binary Path: $($serviceInfo | Where-Object { $_ -like '*BINARY_PATH_NAME*' })"
} else {
    Write-Host "Service not found!" -ForegroundColor Red
}

# 4. Check port 5432
Write-Host "`nChecking port 5432:" -ForegroundColor Yellow
$portCheck = Test-NetConnection -ComputerName localhost -Port 5432 -WarningAction SilentlyContinue
Write-Host "Port 5432 is: " -NoNewline
if ($portCheck.TcpTestSucceeded) {
    Write-Host "OPEN" -ForegroundColor Green
} else {
    Write-Host "CLOSED" -ForegroundColor Red
}

# 5. Check data directory permissions
Write-Host "`nChecking data directory permissions:" -ForegroundColor Yellow
$acl = Get-Acl $PG_DATA -ErrorAction SilentlyContinue
if ($acl) {
    $acl.Access | ForEach-Object {
        Write-Host "Identity: $($_.IdentityReference)"
        Write-Host "Rights: $($_.FileSystemRights)"
    }
} else {
    Write-Host "Could not get permissions!" -ForegroundColor Red
}

# 6. Display postgresql.conf content
Write-Host "`nPostgresql.conf settings:" -ForegroundColor Yellow
if (Test-Path "$PG_DATA\postgresql.conf") {
    Get-Content "$PG_DATA\postgresql.conf" | Where-Object { $_ -match '^[^#]' -and $_ -match '\S' }
} else {
    Write-Host "postgresql.conf not found!" -ForegroundColor Red
}

# 7. Display pg_hba.conf content
Write-Host "`npg_hba.conf settings:" -ForegroundColor Yellow
if (Test-Path "$PG_DATA\pg_hba.conf") {
    Get-Content "$PG_DATA\pg_hba.conf" | Where-Object { $_ -match '^[^#]' -and $_ -match '\S' }
} else {
    Write-Host "pg_hba.conf not found!" -ForegroundColor Red
}

# 8. Try to start service if it's not running
if ($service -and $service.Status -ne 'Running') {
    Write-Host "`nAttempting to start service..." -ForegroundColor Yellow
    Start-Service $SERVICE_NAME
    Start-Sleep -Seconds 5
    $service.Refresh()
    Write-Host "Service status after start attempt: $($service.Status)"
}

# 9. Test PostgreSQL connection
Write-Host "`nTesting PostgreSQL connection:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"

Write-Host "`nDiagnostic complete!" -ForegroundColor Cyan
