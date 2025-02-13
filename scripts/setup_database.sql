-- Create the database if it doesn't exist
CREATE DATABASE rag_doc_analyzer;

-- Connect to the database
\c rag_doc_analyzer

-- Create the extension
CREATE EXTENSION IF NOT EXISTS vector;
