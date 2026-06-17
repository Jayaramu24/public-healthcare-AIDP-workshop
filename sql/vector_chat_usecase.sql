-- Chat with data and documents use case.
--
-- The workshop playbook is provided as:
--   documents/MPHA_Winter_Respiratory_Response_Playbook.docx
-- AIDP or a document-processing job extracts text, chunks it, creates embeddings,
-- and stages the generated chunk context into the Gold document-chat objects.
-- In a live AI Lakehouse setup, use your approved embedding model and vector index.

CREATE TABLE mpha_doc_chunk_vector_stage (
  document_id VARCHAR2(80),
  chunk_id VARCHAR2(120),
  page_number NUMBER,
  section_title VARCHAR2(240),
  chunk_text CLOB,
  embedding_model VARCHAR2(80),
  embedding_json CLOB
);

-- Optional vector-native table pattern for environments with vector support.
-- Load or generate the VECTOR column with the embedding model approved for the tenancy.
CREATE TABLE mpha_doc_chunk_vector_index (
  document_id VARCHAR2(80),
  chunk_id VARCHAR2(120) PRIMARY KEY,
  page_number NUMBER,
  section_title VARCHAR2(240),
  chunk_text CLOB,
  embedding VECTOR(16, FLOAT32)
);

-- Example retrieval context for a prompt such as:
-- "Which districts should receive mobile clinic sessions this week?"
SELECT
  c.chunk_id,
  c.page_number,
  c.section_title,
  DBMS_LOB.SUBSTR(c.chunk_text, 900, 1) AS retrieved_context
FROM mpha_gold_document_chat_context c
WHERE LOWER(c.chunk_text) LIKE '%mobile clinic%'
   OR LOWER(c.chunk_text) LIKE '%spatial%'
   OR LOWER(c.chunk_text) LIKE '%immunization%'
FETCH FIRST 5 ROWS ONLY;

-- Example structured context that can be supplied alongside retrieved chunks.
SELECT
  district_name,
  public_health_pressure_index,
  residents_per_facility,
  spatial_business_insight
FROM mpha_gold_spatial_access_insights
WHERE residents_per_facility >= 100000
   OR public_health_pressure_index >= 45
ORDER BY public_health_pressure_index DESC, residents_per_facility DESC;

-- Example answer assembly context for an application layer.
SELECT
  s.district_name,
  s.spatial_business_insight,
  c.section_title,
  c.page_number
FROM mpha_gold_spatial_access_insights s
CROSS JOIN mpha_gold_document_chat_context c
WHERE s.spatial_business_insight LIKE 'Prioritize%'
  AND c.section_title IN ('4. Immunization Equity Play', '6. Spatial Response Model', '10. Chat with Data and Documents')
ORDER BY s.district_name, c.page_number;
