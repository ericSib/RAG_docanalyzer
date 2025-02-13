# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "Configuration des permissions pour NetworkService..." -ForegroundColor Yellow

# Ajout des droits nécessaires
$dataPath = "C:\Program Files\PostgreSQL\16\data"
$acl = Get-Acl $dataPath

# Ajouter NT AUTHORITY\NetworkService
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "NT AUTHORITY\NetworkService",
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$acl.AddAccessRule($rule)

Set-Acl -Path $dataPath -AclObject $acl

Write-Host "Permissions ajoutées avec succès !" -ForegroundColor Green
Write-Host "Appuyez sur une touche pour continuer..."
pause
