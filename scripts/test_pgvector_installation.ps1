# Ajout du chemin de PostgreSQL à PATH
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

Write-Host "Test de l'installation de pgvector..." -ForegroundColor Yellow

# Vérifier si l'extension est disponible
Write-Host "`n1. Vérification des extensions disponibles :"
& psql -U postgres -d rag_doc_analyzer -c "\dx"

# Exécuter le script de test
Write-Host "`n2. Exécution des tests pgvector..."
& psql -U postgres -d rag_doc_analyzer -f ".\scripts\test_pgvector.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nTests pgvector exécutés avec succès !" -ForegroundColor Green
    
    # Afficher la table de test
    Write-Host "`nContenu de la table test_embeddings :"
    & psql -U postgres -d rag_doc_analyzer -c "SELECT * FROM test_embeddings;"
} else {
    Write-Host "`nErreur lors des tests pgvector." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
