-- Activer l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Créer une table de test avec un champ vectoriel
CREATE TABLE test_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(3)
);

-- Insérer quelques vecteurs de test
INSERT INTO test_embeddings (content, embedding) VALUES
    ('test1', '[1,2,3]'),
    ('test2', '[4,5,6]'),
    ('test3', '[7,8,9]');

-- Créer un index pour la recherche de similarité
CREATE INDEX ON test_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Tester une recherche par similarité
SELECT content, embedding <-> '[1,2,3]' as distance
FROM test_embeddings
ORDER BY embedding <-> '[1,2,3]'
LIMIT 5;
