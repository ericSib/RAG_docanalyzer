-- Test de recherche par similarité sur le document complet
WITH query_embedding AS (
    SELECT array_fill(0.1::float4, ARRAY[1536])::vector AS vec
)
SELECT 
    id,
    title,
    LEFT(content, 50) as content_preview,
    1 - (content_embedding <-> query_embedding.vec) as cosine_similarity
FROM documents, query_embedding
ORDER BY content_embedding <-> query_embedding.vec
LIMIT 5;

-- Test de recherche par similarité sur les chunks
WITH query_embedding AS (
    SELECT array_fill(0.2::float4, ARRAY[1536])::vector AS vec
)
SELECT 
    dc.id as chunk_id,
    d.title as document_title,
    LEFT(dc.chunk_text, 50) as chunk_preview,
    1 - (dc.chunk_embedding <-> query_embedding.vec) as cosine_similarity
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id,
query_embedding
ORDER BY dc.chunk_embedding <-> query_embedding.vec
LIMIT 5;
