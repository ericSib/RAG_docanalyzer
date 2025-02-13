# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

Write-Host "PostgreSQL Permissions Audit Tool" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Configuration
$PG_HOME = "C:\Program Files\PostgreSQL\16"
$PG_DATA = "$PG_HOME\data"
$IMPORTANT_DIRS = @(
    @{Path = $PG_HOME; Name = "PostgreSQL Home"},
    @{Path = $PG_DATA; Name = "Data Directory"},
    @{Path = "$PG_HOME\bin"; Name = "Binaries"},
    @{Path = "$PG_HOME\lib"; Name = "Libraries"},
    @{Path = "$PG_HOME\share"; Name = "Share"},
    @{Path = "$PG_DATA\log"; Name = "Logs"}
)

function Format-FileSystemRights {
    param([System.Security.AccessControl.FileSystemRights]$Rights)
    
    $rightsStr = $Rights.ToString()
    if ($rightsStr -match "^\d+$") {
        switch ([int]$rightsStr) {
            268435456 { "GenericAll" }
            -1610612736 { "ReadAndExecute" }
            default { $rightsStr }
        }
    } else {
        $rightsStr
    }
}

function Check-DirectoryPermissions {
    param(
        [string]$Path,
        [string]$Name
    )
    
    Write-Host "`n=== $Name ($Path) ===" -ForegroundColor Yellow
    
    if (-not (Test-Path $Path)) {
        Write-Host "Directory does not exist!" -ForegroundColor Red
        return
    }
    
    try {
        $acl = Get-Acl $Path
        Write-Host "`nOwner: $($acl.Owner)"
        Write-Host "Group: $($acl.Group)"
        Write-Host "`nAccess Rules:"
        Write-Host "============="
        
        $acl.Access | ForEach-Object {
            $rights = Format-FileSystemRights $_.FileSystemRights
            Write-Host "Identity: $($_.IdentityReference)"
            Write-Host "Rights: $rights"
            Write-Host "Type: $($_.AccessControlType)"
            Write-Host "Inherited: $($_.IsInherited)"
            Write-Host "---"
        }
        
        # Check if NetworkService has access
        $hasNetworkService = $acl.Access | Where-Object { $_.IdentityReference -like "*NetworkService*" }
        if (-not $hasNetworkService) {
            Write-Host "WARNING: NetworkService account does not have explicit permissions" -ForegroundColor Yellow
        }
        
        # Check if current user has access
        $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        $hasCurrentUser = $acl.Access | Where-Object { $_.IdentityReference -eq $currentUser }
        if (-not $hasCurrentUser) {
            Write-Host "WARNING: Current user does not have explicit permissions" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Error getting permissions: $_" -ForegroundColor Red
    }
}

# Check service account
Write-Host "`nChecking PostgreSQL Service Account:" -ForegroundColor Yellow
$service = Get-WmiObject win32_service | Where-Object { $_.Name -eq "postgresql-x64-16" }
if ($service) {
    Write-Host "Service Account: $($service.StartName)"
} else {
    Write-Host "PostgreSQL service not found!" -ForegroundColor Red
}

# Check directory permissions
foreach ($dir in $IMPORTANT_DIRS) {
    Check-DirectoryPermissions -Path $dir.Path -Name $dir.Name
}

# Check specific files
Write-Host "`n=== Important Files ===" -ForegroundColor Yellow
$IMPORTANT_FILES = @(
    "$PG_DATA\postgresql.conf",
    "$PG_DATA\pg_hba.conf",
    "$PG_HOME\bin\postgres.exe",
    "$PG_HOME\bin\pg_ctl.exe"
)

foreach ($file in $IMPORTANT_FILES) {
    Write-Host "`nFile: $file"
    if (Test-Path $file) {
        $acl = Get-Acl $file
        Write-Host "Owner: $($acl.Owner)"
        Write-Host "Permissions:"
        $acl.Access | ForEach-Object {
            $rights = Format-FileSystemRights $_.FileSystemRights
            Write-Host "- $($_.IdentityReference): $rights"
        }
    } else {
        Write-Host "File does not exist!" -ForegroundColor Red
    }
}

Write-Host "`nPermissions audit complete!" -ForegroundColor Green
