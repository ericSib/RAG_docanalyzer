-- Insertion d'un document de test avec son embedding
INSERT INTO documents (
    title,
    content,
    mime_type,
    content_embedding,
    metadata
) VALUES (
    'Test Document',
    'Ceci est un document de test pour vérifier le fonctionnement des embeddings. ' ||
    'Il contient plusieurs phrases qui seront divisées en chunks. ' ||
    'Nous allons tester la recherche sémantique sur ce contenu.',
    'text/plain',
    array_fill(0.1::float4, ARRAY[1536]),  -- Crée un vecteur de dimension 1536 rempli de 0.1
    '{"source": "test", "language": "fr"}'::jsonb
) RETURNING id;

-- Insertion de chunks de test
INSERT INTO document_chunks (
    document_id,
    chunk_text,
    chunk_embedding,
    chunk_metadata
) VALUES 
(
    currval('documents_id_seq'),
    'Ceci est un document de test pour vérifier le fonctionnement des embeddings.',
    array_fill(0.2::float4, ARRAY[1536]),
    '{"position": 1, "tokens": 12}'::jsonb
),
(
    currval('documents_id_seq'),
    'Il contient plusieurs phrases qui seront divisées en chunks.',
    array_fill(0.3::float4, ARRAY[1536]),
    '{"position": 2, "tokens": 10}'::jsonb
),
(
    currval('documents_id_seq'),
    'Nous allons tester la recherche sémantique sur ce contenu.',
    array_fill(0.4::float4, ARRAY[1536]),
    '{"position": 3, "tokens": 9}'::jsonb
);

-- Test de recherche par similarité sur le document complet
SELECT 
    id,
    title,
    content,
    1 - (content_embedding <=> array_fill(0.1::float4, ARRAY[1536])) as cosine_similarity
FROM documents
ORDER BY content_embedding <=> array_fill(0.1::float4, ARRAY[1536])
LIMIT 5;

-- Test de recherche par similarité sur les chunks
SELECT 
    dc.id as chunk_id,
    d.title as document_title,
    dc.chunk_text,
    1 - (dc.chunk_embedding <=> array_fill(0.2::float4, ARRAY[1536])) as cosine_similarity
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id
ORDER BY dc.chunk_embedding <=> array_fill(0.2::float4, ARRAY[1536])
LIMIT 5;
