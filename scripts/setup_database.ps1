# Set PostgreSQL path
$env:PGPASSWORD = "admin123"
$psql = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
$createdb = "C:\Program Files\PostgreSQL\16\bin\createdb.exe"

Write-Host "Creating database..." -ForegroundColor Green
& $createdb -U postgres rag_doc_analyzer

Write-Host "Installing pgvector extension..." -ForegroundColor Green
& $psql -U postgres -d rag_doc_analyzer -c "CREATE EXTENSION IF NOT EXISTS vector;"

Write-Host "Database setup completed!" -ForegroundColor Green
