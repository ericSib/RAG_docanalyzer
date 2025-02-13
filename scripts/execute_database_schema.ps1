# Ajout du chemin de PostgreSQL à PATH
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

Write-Host "Création de la base de données et du schéma..." -ForegroundColor Yellow

# Création de la base de données
Write-Host "1. Création de la base de données rag_doc_analyzer..."
& psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS rag_doc_analyzer;"
& psql -U postgres -d postgres -c "CREATE DATABASE rag_doc_analyzer WITH ENCODING='UTF8' LC_COLLATE='French_France.1252' LC_CTYPE='French_France.1252' TEMPLATE=template0;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Base de données créée avec succès." -ForegroundColor Green
    
    # Exécution du script SQL pour créer les tables et les rôles
    Write-Host "`n2. Création des tables et des rôles..."
    & psql -U postgres -d rag_doc_analyzer -f ".\scripts\init_database_schema.sql"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Schéma de base de données créé avec succès !" -ForegroundColor Green
        
        Write-Host "`nListe des tables créées :" -ForegroundColor Yellow
        & psql -U postgres -d rag_doc_analyzer -c "\dt"
        
        Write-Host "`nListe des rôles :" -ForegroundColor Yellow
        & psql -U postgres -d rag_doc_analyzer -c "\du"
    } else {
        Write-Host "Erreur lors de la création du schéma." -ForegroundColor Red
    }
} else {
    Write-Host "Erreur lors de la création de la base de données." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
