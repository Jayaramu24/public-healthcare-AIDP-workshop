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
2. In AIDP, use one shared workspace and one folder per participant under `Participants/<participant_id>`.
3. Place the notebooks in the participant folder being tested.
4. In Autonomous AI Lakehouse, create or confirm the assigned participant schema, such as `MPHA_P17`, then run `sql/admin_prepare_participant_claims_star_schemas.sql` as `ADMIN` for the full classroom setup.
5. Refresh the AIDP external catalog `goldailh` and confirm the participant schema is visible.
6. Run Bronze, Silver, Gold staging, and AI Lakehouse load notebooks in the workshop sequence. Set `participant_id`, `target_catalog = "goldailh"`, and the assigned `target_schema` before running.
7. Validate the Claims star schema using `sql/claims_star_validation.sql`.
8. For the Round 2 extension, run `sql/create_ai_lakehouse_claims_context_extension.sql`, then run the Silver and Gold context extension notebooks, and validate with `sql/claims_context_extension_validation.sql`.
9. Use the workflow files only after the individual notebooks have been tested successfully.
