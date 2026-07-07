# Public Healthcare AIDP Workshop Offline Test Bundle

Use this bundle with `workshop_guide.pdf` when testing the workshop without the GitHub Pages site.

## Included folders

- `data/raw/` - five CSV source datasets for claims, membership, disbursement, facility operations, provider accreditation, district health profile, and population health.
- `data/raw_json/` - JSON Lines capacity and operations event feed.
- `data/raw_spatial/` - GeoJSON service-area boundaries for spatial insights.
- `documents/` - MPHA policy/playbook document used for the RAG knowledge base.
- `notebooks/` - AIDP notebooks and PySpark notebook source files for Bronze, Silver, Gold, AI Lakehouse load, Round 2 JSON/spatial context enrichment, and ML scoring.
- `sql/` - AI Lakehouse schema creation, context extension, validation, analytics, spatial, and vector SQL scripts.
- `workflows/` - incremental medallion workflow definition and companion notes.

## Suggested test order

1. Upload the raw CSV, JSON, spatial, and document files to the Object Storage folders described in the PDF guide.
2. Import the Bronze, Silver, Gold, AI Lakehouse load, and ML notebooks into the AIDP workspace.
3. Run the SQL schema scripts needed for the Claims star schema and optional Facilities star schema.
4. Run the notebooks in the workshop sequence.
5. Validate the Claims star schema using `sql/claims_star_validation.sql`.
6. For the Round 2 extension, run `sql/create_ai_lakehouse_claims_context_extension.sql`, then run the Silver and Gold context extension notebooks, and validate with `sql/claims_context_extension_validation.sql`.
7. Use the workflow files only after the individual notebooks have been tested successfully.
