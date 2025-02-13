-- Ajout du champ embedding à la table documents
ALTER TABLE documents 
ADD COLUMN content_embedding vector(1536);

-- Création d'un index pour la recherche par similarité
CREATE INDEX idx_documents_embedding ON documents 
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

-- Table pour stocker les chunks de documents avec leurs embeddings
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_text TEXT,
    chunk_embedding vector(1536),
    chunk_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour la recherche par similarité sur les chunks
CREATE INDEX idx_document_chunks_embedding ON document_chunks 
USING ivfflat (chunk_embedding vector_cosine_ops)
WITH (lists = 100);

-- Ajout des permissions pour le rôle rag_app_user
GRANT SELECT, INSERT, UPDATE ON document_chunks TO rag_app_user;
