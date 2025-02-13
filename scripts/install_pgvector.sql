-- Enable the PostgreSQL extension repository
CREATE EXTENSION IF NOT EXISTS adminpack;

-- Create the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
