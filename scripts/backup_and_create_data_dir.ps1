# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$baseDir = "C:\Program Files\PostgreSQL\16"
$dataDir = "$baseDir\data"
$backupDir = "$baseDir\data_old_$timestamp"

Write-Host "Sauvegarde du répertoire data..." -ForegroundColor Yellow
if (Test-Path $dataDir) {
    Write-Host "Déplacement de $dataDir vers $backupDir"
    Move-Item -Path $dataDir -Destination $backupDir -Force
    Write-Host "Sauvegarde terminée dans : $backupDir" -ForegroundColor Green
} else {
    Write-Host "Le répertoire data n'existe pas." -ForegroundColor Yellow
}

Write-Host "`nCréation d'un nouveau répertoire data..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null

# Configuration des permissions pour NetworkService
Write-Host "`nConfiguration des permissions..." -ForegroundColor Yellow
$acl = Get-Acl $dataDir
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "NT AUTHORITY\NetworkService",
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl -Path $dataDir -AclObject $acl

Write-Host "`nOpération terminée avec succès !" -ForegroundColor Green
Write-Host "Nouveau répertoire data : $dataDir"
Write-Host "Sauvegarde : $backupDir"

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
