# Ajout du chemin de PostgreSQL à PATH
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

Write-Host "Mise à jour du schéma de la base de données..." -ForegroundColor Yellow

# Exécution du script SQL
Write-Host "`n1. Ajout des champs et tables pour les embeddings..."
& psql -U postgres -d rag_doc_analyzer -f ".\scripts\add_embeddings_schema.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSchéma mis à jour avec succès !" -ForegroundColor Green
    
    Write-Host "`nStructure de la table documents :"
    & psql -U postgres -d rag_doc_analyzer -c "\d documents"
    
    Write-Host "`nStructure de la table document_chunks :"
    & psql -U postgres -d rag_doc_analyzer -c "\d document_chunks"
    
    Write-Host "`nIndex créés :"
    & psql -U postgres -d rag_doc_analyzer -c "\di"
    
    Write-Host "`nPermissions du rôle rag_app_user :"
    & psql -U postgres -d rag_doc_analyzer -c "\z"
} else {
    Write-Host "`nErreur lors de la mise à jour du schéma." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
