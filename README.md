# Public Healthcare AIDP Workshop

![Workshop preview](assets/public-health-dashboard-preview.png)

This repository contains a shareable workshop kit modeled after an Oracle LiveLabs-style analytics workshop, adapted for a fictional public healthcare organization. It is designed for workshop execution teams, solution engineers, and customer-facing teams who want a ready-to-run healthcare lakehouse scenario with curated data, Spark notebooks, SQL assets, dashboards, and a polished guide.

## Scenario At A Glance

**Organization:** Metro Public Health Authority (MPHA)  
**Objective:** Improve access to care, operational resilience, and program governance using a lakehouse built on Oracle AI Data Platform and Autonomous AI Lakehouse.

The business story blends four recognizable healthcare administration domains:

- Claims
- Disbursement
- Membership
- Healthcare Provider Accreditation

The end-to-end flow moves from raw operational data into a medallion architecture, then into a Gold dimensional model for Oracle Analytics Cloud and AI-assisted insights.

## Quick Start

1. Open the shareable workshop landing page: [index.html](index.html)
2. Use the formatted workshop guide for delivery: [workshop_guide.pdf](workshop_guide.pdf)
3. Review the detailed hands-on instructions: [workshop_guide.md](workshop_guide.md)
4. Run the notebooks in this order:
   - [notebooks/aidp_bronze_pyspark.py](notebooks/aidp_bronze_pyspark.py)
   - [notebooks/aidp_silver_pyspark.py](notebooks/aidp_silver_pyspark.py)
   - [notebooks/aidp_gold_pyspark.py](notebooks/aidp_gold_pyspark.py)
5. Use the Gold schema SQL in AI Lakehouse:
   - [sql/create_ai_lakehouse_dimensional_gold_schema.sql](sql/create_ai_lakehouse_dimensional_gold_schema.sql)

If you want to preview the HTML locally in a browser:

```bash
cd public_healthcare_lakehouse_workshop
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.

## What The Execution Team Gets

- A LiveLabs-style HTML workshop page for sharing and facilitation
- A professionally formatted PDF guide for offline delivery
- A compact raw source set with healthcare-relevant business flavor
- Separate Bronze, Silver, and Gold Spark notebooks for AIDP
- A Gold star schema designed for AI Lakehouse and OAC
- Interactive dashboard mockups, spatial insight examples, and vector-chat patterns
- Optional extension labs for GoldenGate and Kafka-compatible streaming

## Raw Source Datasets

The raw landing zone has been intentionally tuned down to a compact set:

| Dataset | Format | Purpose |
|---|---|---|
| `claims_membership_disbursement.csv` | CSV | Claims activity, member program status, payment disbursement, and reimbursement context |
| `district_health_profile.csv` | CSV | District-level demographics, risk, and access coverage context |
| `facility_operations_daily.csv` | CSV | Daily operational measures such as wait time, bed occupancy, and staffing pressure |
| `facility_provider_master.csv` | CSV | Facility, provider, and accreditation reference data |
| `population_health_weekly.csv` | CSV | Weekly outreach, immunization, and respiratory surveillance metrics |
| `facility_capacity_events.jsonl` | JSONL | Semi-structured capacity and escalation event feed |
| `healthcare_service_areas.geojson` | GeoJSON | Spatial service areas, districts, facilities, and catchment relationships |
| `MPHA_Winter_Respiratory_Response_Playbook.docx` | Document | Multi-page operating playbook used for vectorization and chat-with-documents |

## Medallion Design

The workshop uses a classic medallion progression with Oracle AI Data Platform driving the refinement flow.

### Bronze

- Ingest raw CSV, JSONL, GeoJSON, and document metadata
- Preserve source fidelity and audit fields
- Standardize ingestion timestamps, source file tags, and landing schemas

### Silver

- Cleanse and standardize codes, dates, provider status, and district references
- Join operational, claims, membership, disbursement, and accreditation records
- Derive quality flags, service-area mappings, and conformed business entities
- Prepare vectorization metadata for the document-chat use case

### Gold

- Publish a dimensional model in Autonomous AI Lakehouse
- Use shared dimensions and facts for OAC and AI workloads
- Support executive, operational, spatial, and document-assisted analytics

The recommended Gold layer is a dimensional star schema with shared conformed dimensions and business-serving views:

- `dim_date`
- `dim_district`
- `dim_facility`
- `dim_provider`
- `dim_program`
- `dim_service_line`
- `fact_claims`
- `fact_membership`
- `fact_disbursement`
- `fact_operations`
- `fact_population_health`

Facility-grain facts also carry `district_key`, so OAC joins directly from facts to both `dim_facility` and `dim_district` without dimension-to-dimension dependencies.

Reference material:

- [medallion_architecture.md](medallion_architecture.md)
- [sql/create_ai_lakehouse_dimensional_gold_schema.sql](sql/create_ai_lakehouse_dimensional_gold_schema.sql)
- [data/gold_dimensional/](data/gold_dimensional/)

## Dashboard And Insight Coverage

The OAC wireframes and workshop narrative cover:

- Executive care access and operational resilience
- Claims and disbursement monitoring
- Membership growth, lapse, and eligibility risk
- Provider accreditation readiness and expiry tracking
- Spatial access analysis using district and facility catchments
- Chat with structured data and vectorized healthcare operating documents

Useful references:

- [dashboard_spec.md](dashboard_spec.md)
- [sql/analytics_queries.sql](sql/analytics_queries.sql)
- [sql/spatial_insights.sql](sql/spatial_insights.sql)
- [sql/vector_chat_usecase.sql](sql/vector_chat_usecase.sql)

## Notebook Sequence

Use the Spark assets as separate notebooks in Oracle AI Data Platform:

- [notebooks/aidp_bronze_pyspark.py](notebooks/aidp_bronze_pyspark.py)  
  Loads raw datasets and writes Bronze Delta tables.

- [notebooks/aidp_silver_pyspark.py](notebooks/aidp_silver_pyspark.py)  
  Cleanses, joins, and refines Bronze data into conformed Silver tables.

- [notebooks/aidp_gold_pyspark.py](notebooks/aidp_gold_pyspark.py)  
  Produces Gold-ready dimensional outputs and business-serving views.

- [notebooks/aidp_refinement_pyspark.py](notebooks/aidp_refinement_pyspark.py)  
  Retained as a single-script reference version of the medallion flow.

## Repository Map

- [index.html](index.html) - shareable workshop landing page
- [workshop_guide.md](workshop_guide.md) - detailed facilitator guide
- [workshop_guide.pdf](workshop_guide.pdf) - downloadable formatted guide
- [data_dictionary.md](data_dictionary.md) - business definitions and column details
- [manifest.json](manifest.json) - generated artifact manifest
- [optional_labs/](optional_labs/) - real-time and streaming extension labs
- [github_migration.md](github_migration.md) - repository handoff instructions

## Optional Labs

- [optional_labs/real_time_analytics_golden_gate.md](optional_labs/real_time_analytics_golden_gate.md)
- [optional_labs/stream_analytics_kafka_aidp.md](optional_labs/stream_analytics_kafka_aidp.md)

These labs extend the core workshop into:

- Real-time analytics using OCI GoldenGate
- Stream analytics using Kafka-compatible streaming through AIDP

## Data Privacy

All data in this repository is synthetic and intended for workshop use only. It contains no real patient names, precise addresses, medical record numbers, or protected health information.

## GitHub Handoff

If this kit is being copied, rebranded, or moved into another repository, use [github_migration.md](github_migration.md) for the handoff steps.
