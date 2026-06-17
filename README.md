# Public Healthcare Lakehouse Analytics Workshop

This kit recreates the structure of the referenced Oracle LiveLabs analytics workshop for a public healthcare organization.

## Workshop Scenario

**Organization:** Metro Public Health Authority (MPHA), a fictional public healthcare network.

**Business use case:** Improve equitable access to care and operational resilience by analyzing clinic demand, emergency wait times, bed occupancy, staffing pressure, immunization uptake, respiratory surveillance, service-quality events, claims adjudication, public-program disbursement, membership eligibility, and healthcare provider accreditation.

The workshop mirrors the original lakehouse analytics flow:

1. Load a streamlined raw source set into cloud storage: five CSV datasets, one JSONL event dataset, one GeoJSON spatial dataset, and one document.
2. Create Bronze and Silver Delta layers with Spark and Delta Lake in Oracle AI Data Platform.
3. Set up the Gold business-serving layer in Autonomous AI Lakehouse as a dimensional snowflake / fact constellation schema.
4. Build executive, spatial, document-chat, and operations dashboards in Oracle Analytics Cloud.
5. Use generative analytics prompts to summarize risks and actions from structured data and vectorized documents.

## Contents

- `workshop_guide.md` - full hands-on lab guide.
- `workshop_guide.pdf` - professionally formatted downloadable PDF guide for the execution team.
- `index.html` - shareable LiveLabs-style landing page for the execution team.
- `medallion_architecture.md` - Bronze, Silver, and Gold layer data design and transformation logic.
- `data/raw/` - five synthetic CSV source files for ingestion.
- `data/raw_json/` - one synthetic JSONL source event dataset for capacity signals.
- `data/raw_spatial/` - one synthetic GeoJSON source with district, facility, and catchment features.
- `documents/` - one synthetic 13-page healthcare operating playbook for document-vector labs.
- `data/streaming/` - sample Kafka-compatible wait-time events for optional stream analytics.
- `data/curated/` - generated Silver-style sample outputs from the original data generation step.
- `data/gold/` - flat AI Lakehouse Gold mart samples retained for quick validation.
- `data/gold_dimensional/` - recommended Gold snowflake schema samples with shared dimensions and fact tables.
- `data_dictionary.md` - columns, grains, and metric definitions.
- `sql/create_ai_lakehouse_gold_layer.sql` - flat Gold mart setup retained for comparison.
- `sql/create_ai_lakehouse_dimensional_gold_schema.sql` - recommended AI Lakehouse dimensional Gold setup with OAC serving views.
- `sql/analytics_queries.sql` - sample business queries for validation and OAC datasets.
- `sql/spatial_insights.sql` - spatial planning queries for mobile clinic and catchment decisions.
- `sql/vector_chat_usecase.sql` - document-vector and chat-with-data query patterns.
- `sql/realtime_gold_tables.sql` - optional real-time and streaming serving objects.
- `notebooks/aidp_bronze_pyspark.py` - Bronze ingestion notebook for AIDP.
- `notebooks/aidp_silver_pyspark.py` - Silver refinement notebook for AIDP.
- `notebooks/aidp_gold_pyspark.py` - Gold staging notebook for AI Lakehouse and OAC serving outputs.
- `notebooks/aidp_refinement_pyspark.py` - legacy combined notebook retained as a single-script reference.
- `notebooks/aidp_kafka_streaming_pyspark.py` - optional Kafka-compatible streaming notebook script.
- `optional_labs/` - optional GoldenGate and Kafka/AIDP lab runbooks.
- `github_migration.md` - GitHub handoff steps and push commands.
- `tools/create_simplified_source_datasets.py` - validation helper for the simplified raw source set.
- `tools/create_dimensional_gold_schema.py` - reproducible dimensional Gold schema sample generator.
- `tools/create_public_healthcare_page_asset.py` - reproducible landing-page preview image generator.
- `tools/create_workshop_guide_pdf.py` - reproducible PDF guide generator.
- `dashboard_spec.md` - OAC dashboard layout and recommended visuals.
- `manifest.json` - generated dataset manifest.

## Data Privacy

All data is synthetic. The dataset contains no patient names, addresses, medical record numbers, exact birth dates, or protected health information. Claims and membership records use synthetic identifiers and coarse service categories for workshop analytics only.

## GitHub Handoff

Use [github_migration.md](github_migration.md) if you want to move this workshop kit into your own GitHub repository and keep the Bronze, Silver, and Gold notebook sequence intact.

## Suggested Workshop Length

3 hours for the core workshop, plus optional extension labs:

- Lab 1: Create the healthcare lakehouse and ingest raw data - 45 minutes
- Lab 2: Build Bronze and Silver layers in AIDP - 75 minutes
- Lab 3: Set up AI Lakehouse Gold and build OAC insights - 60 minutes
- Optional Lab 4: Real-time analytics using OCI GoldenGate - 45 to 60 minutes
- Optional Lab 5: Stream analytics using Kafka-compatible streaming through AIDP - 45 to 60 minutes
