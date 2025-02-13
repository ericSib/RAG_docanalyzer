-- Mise à jour du schéma pour utiliser des vecteurs de 512 dimensions
BEGIN;

-- Suppression des anciennes tables si elles existent
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- Création de l'extension vector si elle n'existe pas
CREATE EXTENSION IF NOT EXISTS vector;

-- Table des documents
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_embedding vector(512) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des chunks de documents
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(512) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour la recherche par similarité
CREATE INDEX document_embedding_idx ON documents USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX chunk_embedding_idx ON document_chunks USING ivfflat (chunk_embedding vector_cosine_ops);

-- Permissions pour l'utilisateur de l'application
GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO rag_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON document_chunks TO rag_app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rag_app_user;

COMMIT;
