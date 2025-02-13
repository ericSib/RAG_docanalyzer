# Nécessite des privilèges administratifs
Write-Host "Activation de la prise en charge des chemins longs dans Windows..." -ForegroundColor Yellow

try {
    # Vérification si la clé de registre existe
    $longPathsEnabled = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -ErrorAction SilentlyContinue

    if ($null -eq $longPathsEnabled) {
        Write-Host "La clé de registre n'existe pas. Création..."
        New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
    }
    else {
        Write-Host "Mise à jour de la clé de registre..."
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
    }

    Write-Host "`nLa prise en charge des chemins longs a été activée avec succès !" -ForegroundColor Green
    Write-Host "Veuillez redémarrer votre ordinateur pour que les changements prennent effet." -ForegroundColor Yellow
}
catch {
    Write-Host "`nErreur : Ce script doit être exécuté en tant qu'administrateur." -ForegroundColor Red
    Write-Host "Veuillez exécuter PowerShell en tant qu'administrateur et réessayer." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
