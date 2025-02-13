# Ajout du chemin de PostgreSQL à PATH
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

Write-Host "Test de recherche par similarité..." -ForegroundColor Yellow

# Exécution du script SQL
Write-Host "`n1. Recherche de documents et chunks similaires..."
& psql -U postgres -d rag_doc_analyzer -f ".\scripts\test_similarity_search.sql"

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
