# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

$dataDir = "C:\Program Files\PostgreSQL\16\data"
$networkService = "NT AUTHORITY\NetworkService"

Write-Host "Configuration des permissions sur le répertoire data..." -ForegroundColor Yellow

# 1. Prendre possession du répertoire
Write-Host "1. Prise de possession du répertoire..."
takeown /F $dataDir /R /D Y | Out-Null

# 2. Donner le contrôle total à SYSTEM et Administrateurs
Write-Host "2. Configuration des permissions de base..."
$acl = Get-Acl $dataDir
$acl.SetAccessRuleProtection($true, $false)  # Désactive l'héritage

# Ajouter SYSTEM avec contrôle total
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "NT AUTHORITY\SYSTEM",
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$acl.AddAccessRule($rule)

# Ajouter Administrators avec contrôle total
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "BUILTIN\Administrators",
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$acl.AddAccessRule($rule)

# 3. Ajouter NetworkService avec les bonnes permissions
Write-Host "3. Configuration des permissions pour NetworkService..."
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $networkService,
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$acl.AddAccessRule($rule)

# 4. Appliquer les permissions
Write-Host "4. Application des nouvelles permissions..."
Set-Acl $dataDir $acl

# 5. Propager les permissions à tous les sous-répertoires et fichiers
Write-Host "5. Propagation des permissions..."
icacls $dataDir /grant:r "${networkService}:(OI)(CI)F" /T /Q
icacls $dataDir /grant:r "NT AUTHORITY\SYSTEM:(OI)(CI)F" /T /Q
icacls $dataDir /grant:r "BUILTIN\Administrators:(OI)(CI)F" /T /Q

Write-Host "`nConfiguration des permissions terminée !" -ForegroundColor Green
Write-Host "Vous pouvez maintenant essayer de redémarrer le service." -ForegroundColor Yellow

pause
