# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    # Relaunch as an elevated process
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "PostgreSQL Complete Fix Tool" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

# Configuration
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# 1. Remove existing service
Write-Host "`nRemoving existing service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue
& sc.exe delete $SERVICE_NAME
Start-Sleep -Seconds 2

# 2. Fix permissions on data directory
Write-Host "`nFixing data directory permissions..." -ForegroundColor Yellow
$acl = Get-Acl $PG_DATA
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("NT AUTHORITY\NetworkService", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.AddAccessRule($rule)
Set-Acl $PG_DATA $acl

# 3. Create new service
Write-Host "`nCreating new service..." -ForegroundColor Yellow
$binPath = "`"$PG_HOME\bin\pg_ctl.exe`" runservice -N `"$SERVICE_NAME`" -D `"$PG_DATA`" -w"
& sc.exe create $SERVICE_NAME binPath= $binPath start= auto DisplayName= "PostgreSQL Server 16"
& sc.exe description $SERVICE_NAME "PostgreSQL Server 16"
& sc.exe config $SERVICE_NAME obj= "NT AUTHORITY\NetworkService"
Start-Sleep -Seconds 2

# 4. Start service
Write-Host "`nStarting service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME
Start-Sleep -Seconds 5

# 5. Verify service
Write-Host "`nVerifying service:" -ForegroundColor Yellow
$service = Get-Service $SERVICE_NAME
Write-Host "Service Status: $($service.Status)"

# 6. Test PostgreSQL connection
Write-Host "`nTesting PostgreSQL connection:" -ForegroundColor Yellow
$env:PGPASSWORD = "admin123"
& "$PG_HOME\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"

Write-Host "`nFix complete!" -ForegroundColor Green
