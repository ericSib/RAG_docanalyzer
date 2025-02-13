# Ajout du chemin de PostgreSQL à PATH
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

Write-Host "Création de la base de données rag_doc_analyzer..." -ForegroundColor Yellow

# Création de la base de données
& psql -U postgres -d postgres -c "CREATE DATABASE rag_doc_analyzer WITH ENCODING='UTF8' LC_COLLATE='French_France.1252' LC_CTYPE='French_France.1252' TEMPLATE=template0;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBase de données créée avec succès !" -ForegroundColor Green
    
    Write-Host "`nListe des bases de données :" -ForegroundColor Yellow
    & psql -U postgres -d postgres -c "\l"
} else {
    Write-Host "`nÉchec de la création de la base de données." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
