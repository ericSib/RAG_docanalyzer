# Ajout du chemin de PostgreSQL à PATH
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

Write-Host "Test d'insertion de document avec embeddings..." -ForegroundColor Yellow

# Exécution du script SQL
Write-Host "`n1. Insertion du document et des chunks..."
& psql -U postgres -d rag_doc_analyzer -f ".\scripts\test_document_insertion.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nTests exécutés avec succès !" -ForegroundColor Green
    
    Write-Host "`nContenu de la table documents :"
    & psql -U postgres -d rag_doc_analyzer -c "SELECT id, title, LEFT(content, 50) as content_preview FROM documents;"
    
    Write-Host "`nContenu de la table document_chunks :"
    & psql -U postgres -d rag_doc_analyzer -c "SELECT id, document_id, LEFT(chunk_text, 50) as chunk_preview, chunk_metadata FROM document_chunks;"
} else {
    Write-Host "`nErreur lors des tests." -ForegroundColor Red
}

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
