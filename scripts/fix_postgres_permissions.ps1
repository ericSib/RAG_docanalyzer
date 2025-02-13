# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "PostgreSQL Permissions Fix Tool" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Configuration
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"
$SERVICE_NAME = "postgresql-x64-16"

# Required accounts
$ACCOUNTS = @(
    "NT AUTHORITY\NetworkService",
    "NT AUTHORITY\SYSTEM",
    "BUILTIN\Administrators",
    [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
)

function Add-DirectoryPermissions {
    param(
        [string]$Path,
        [string]$Name,
        [bool]$IsDataDir = $false
    )
    
    Write-Host "`nSetting permissions for $Name ($Path)..." -ForegroundColor Yellow
    
    if (-not (Test-Path $Path)) {
        Write-Host "Creating directory: $Path"
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
    
    try {
        $acl = Get-Acl $Path
        
        # Remove existing permissions
        $acl.Access | ForEach-Object {
            try {
                $acl.RemoveAccessRule($_) | Out-Null
            } catch {
                Write-Host "Warning: Could not remove rule for $($_.IdentityReference): $_" -ForegroundColor Yellow
            }
        }
        
        # Add new permissions
        foreach ($account in $ACCOUNTS) {
            $rights = if ($IsDataDir) { "FullControl" } else { "ReadAndExecute" }
            $inheritance = if ($IsDataDir) { "ContainerInherit,ObjectInherit" } else { "None" }
            
            $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $account,
                $rights,
                $inheritance,
                "None",
                "Allow"
            )
            
            try {
                $acl.AddAccessRule($rule)
                Write-Host "Added $rights permission for $account"
            } catch {
                Write-Host "Error adding permission for $account: $_" -ForegroundColor Red
            }
        }
        
        # Set ownership to SYSTEM
        $owner = New-Object System.Security.Principal.NTAccount("NT AUTHORITY\SYSTEM")
        $acl.SetOwner($owner)
        
        # Apply the new ACL
        Set-Acl $Path $acl
        Write-Host "Permissions set successfully for $Name" -ForegroundColor Green
    }
    catch {
        Write-Host "Error setting permissions for $Name: $_" -ForegroundColor Red
    }
}

# 1. Stop service if running
Write-Host "`nStopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service $SERVICE_NAME -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 2. Fix permissions for main directories
$IMPORTANT_DIRS = @(
    @{Path = $PG_HOME; Name = "PostgreSQL Home"},
    @{Path = "$PG_HOME\bin"; Name = "Binaries"},
    @{Path = "$PG_HOME\lib"; Name = "Libraries"},
    @{Path = "$PG_HOME\share"; Name = "Share"}
)

foreach ($dir in $IMPORTANT_DIRS) {
    Add-DirectoryPermissions -Path $dir.Path -Name $dir.Name -IsDataDir $false
}

# 3. Fix permissions for data directory and its contents
Add-DirectoryPermissions -Path $PG_DATA -Name "Data Directory" -IsDataDir $true

# Create and set permissions for log directory
$logDir = "$PG_DATA\log"
Add-DirectoryPermissions -Path $logDir -Name "Log Directory" -IsDataDir $true

# 4. Fix service account
Write-Host "`nConfiguring service account..." -ForegroundColor Yellow
try {
    & sc.exe config $SERVICE_NAME obj= "NT AUTHORITY\NetworkService"
    Write-Host "Service account updated successfully" -ForegroundColor Green
}
catch {
    Write-Host "Error updating service account: $_" -ForegroundColor Red
}

# 5. Start service
Write-Host "`nStarting PostgreSQL service..." -ForegroundColor Yellow
Start-Service $SERVICE_NAME
Start-Sleep -Seconds 5

# 6. Verify service status
$service = Get-Service $SERVICE_NAME
Write-Host "`nService Status: $($service.Status)"

Write-Host "`nPermissions fix complete!" -ForegroundColor Green
Write-Host "Please run check_permissions.ps1 to verify the changes." -ForegroundColor Yellow
