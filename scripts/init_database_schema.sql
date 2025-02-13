-- Création de la base de données
CREATE DATABASE rag_doc_analyzer
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TEMPLATE template0;

\c rag_doc_analyzer

-- Création des tables principales
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    file_path VARCHAR(512),
    mime_type VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Table pour les métriques d'analyse
CREATE TABLE document_metrics (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    word_count INTEGER,
    complexity_score FLOAT,
    quality_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Table pour le tracking des versions
CREATE TABLE document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    version_number INTEGER,
    changes_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Création des index
CREATE INDEX idx_documents_title ON documents(title);
CREATE INDEX idx_documents_mime_type ON documents(mime_type);
CREATE INDEX idx_document_metrics_scores ON document_metrics(quality_score, complexity_score);

-- Création des rôles et permissions
CREATE ROLE rag_app_user WITH LOGIN PASSWORD 'ChangeThisPassword123!';
GRANT CONNECT ON DATABASE rag_doc_analyzer TO rag_app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO rag_app_user;
