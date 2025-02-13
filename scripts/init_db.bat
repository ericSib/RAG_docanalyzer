@echo off
SET PGPASSWORD=admin123

echo Creating database...
"C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -h localhost -p 5432 -d postgres -c "CREATE DATABASE rag_doc_analyzer;"

echo Enabling pgvector extension...
"C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -h localhost -p 5432 -d rag_doc_analyzer -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo Database initialization completed.
