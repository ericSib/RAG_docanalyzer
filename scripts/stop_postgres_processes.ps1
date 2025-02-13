# Check if running with admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "Arrêt de tous les processus PostgreSQL..." -ForegroundColor Yellow
$processes = Get-Process -Name postgres* -ErrorAction SilentlyContinue
if ($processes) {
    $processes | ForEach-Object {
        Write-Host "Arrêt du processus : $($_.Name) (PID: $($_.Id))"
        $_ | Stop-Process -Force
    }
    Write-Host "Tous les processus ont été arrêtés." -ForegroundColor Green
} else {
    Write-Host "Aucun processus PostgreSQL en cours d'exécution." -ForegroundColor Green
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
