# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

# Create output file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "C:\DEV\RAG_Doc-analyzer\permissions_audit_$timestamp.txt"
Start-Transcript -Path $outputFile

Write-Host "PostgreSQL Permissions Audit Tool" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)"
Write-Host "Computer: $env:COMPUTERNAME"
Write-Host "Current User: $env:USERNAME"

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
        
        $acl.Access | Sort-Object IdentityReference | ForEach-Object {
            $rights = Format-FileSystemRights $_.FileSystemRights
            Write-Host "`nIdentity: $($_.IdentityReference)"
            Write-Host "Rights: $rights"
            Write-Host "Type: $($_.AccessControlType)"
            Write-Host "Inheritance Flags: $($_.InheritanceFlags)"
            Write-Host "Propagation Flags: $($_.PropagationFlags)"
            Write-Host "Inherited: $($_.IsInherited)"
        }
        
        # Check critical accounts
        $criticalAccounts = @(
            "NT AUTHORITY\NetworkService",
            "NT AUTHORITY\SYSTEM",
            "BUILTIN\Administrators",
            [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        )
        
        Write-Host "`nCritical Accounts Status:"
        Write-Host "======================="
        foreach ($account in $criticalAccounts) {
            $hasAccess = $acl.Access | Where-Object { $_.IdentityReference -like "*$account*" }
            Write-Host "$account : $(if ($hasAccess) { "Present" } else { "Missing" })"
        }
    }
    catch {
        Write-Host "Error getting permissions: $_" -ForegroundColor Red
    }
}

# Check service account
Write-Host "`nPostgreSQL Service Configuration:" -ForegroundColor Yellow
Write-Host "=============================="
$service = Get-WmiObject win32_service | Where-Object { $_.Name -eq "postgresql-x64-16" }
if ($service) {
    Write-Host "Service Name: $($service.Name)"
    Write-Host "Display Name: $($service.DisplayName)"
    Write-Host "Start Name: $($service.StartName)"
    Write-Host "Start Mode: $($service.StartMode)"
    Write-Host "State: $($service.State)"
    Write-Host "Path: $($service.PathName)"
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
    @{Path = "$PG_DATA\postgresql.conf"; Name = "PostgreSQL Configuration"},
    @{Path = "$PG_DATA\pg_hba.conf"; Name = "Client Authentication Configuration"},
    @{Path = "$PG_HOME\bin\postgres.exe"; Name = "PostgreSQL Server Executable"},
    @{Path = "$PG_HOME\bin\pg_ctl.exe"; Name = "PostgreSQL Control Utility"}
)

foreach ($file in $IMPORTANT_FILES) {
    Write-Host "`n--- $($file.Name) ---"
    Write-Host "Path: $($file.Path)"
    if (Test-Path $file.Path) {
        $acl = Get-Acl $file.Path
        Write-Host "Owner: $($acl.Owner)"
        Write-Host "Permissions:"
        $acl.Access | Sort-Object IdentityReference | ForEach-Object {
            $rights = Format-FileSystemRights $_.FileSystemRights
            Write-Host "- $($_.IdentityReference)"
            Write-Host "  Rights: $rights"
            Write-Host "  Inherited: $($_.IsInherited)"
        }
    } else {
        Write-Host "File does not exist!" -ForegroundColor Red
    }
}

Write-Host "`nPermissions audit complete!" -ForegroundColor Green
Write-Host "Results have been saved to: $outputFile" -ForegroundColor Green

Stop-Transcript
