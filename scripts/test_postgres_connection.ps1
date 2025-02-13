# Ajout du chemin de PostgreSQL à PATH
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

Write-Host "Test de connexion à PostgreSQL..." -ForegroundColor Yellow
Write-Host "Exécution : psql -U postgres -d postgres -c `"SELECT version();`"`n"

& psql -U postgres -d postgres -c "SELECT version();"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nConnexion réussie !" -ForegroundColor Green
    
    Write-Host "`nListe des bases de données :" -ForegroundColor Yellow
    & psql -U postgres -d postgres -c "\l"
} else {
    Write-Host "`nÉchec de la connexion." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
