-- Create database if it doesn't exist
CREATE DATABASE rag_doc_analyzer;

-- Connect to the database
\c rag_doc_analyzer;

-- Create the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE rag_doc_analyzer TO postgres;
