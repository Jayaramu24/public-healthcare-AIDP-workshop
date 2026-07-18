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

The end-to-end flow moves from raw operational data into a medallion architecture, then branches into two Gold teaching outcomes: an instructor-led Claims star schema with a provided OAC workbook, and a DIY Facility Access Daily star schema that participants model and visualize on their own.

## Quick Start

1. Open the shareable workshop landing page: [index.html](index.html)
2. Use the single end-to-end runbook for facilitation: [workshop_single_flow.html](workshop_single_flow.html)
3. Use the formatted workshop guide for delivery: [workshop_guide.pdf](workshop_guide.pdf)
4. Review the detailed hands-on instructions: [workshop_guide.md](workshop_guide.md)
5. Run the notebooks in this order:
- [notebooks/aidp_bronze_pyspark.py](notebooks/aidp_bronze_pyspark.py)
- [notebooks/aidp_silver_pyspark.py](notebooks/aidp_silver_pyspark.py)
- [notebooks/aidp_gold_pyspark.py](notebooks/aidp_gold_pyspark.py)
- [notebooks/aidp_claims_star_ai_lakehouse_pyspark.py](notebooks/aidp_claims_star_ai_lakehouse_pyspark.py)
6. Use the Gold schema SQL in AI Lakehouse:
   - [sql/create_ai_lakehouse_claims_star_schema.sql](sql/create_ai_lakehouse_claims_star_schema.sql)
   - [sql/create_ai_lakehouse_facilities_star_schema.sql](sql/create_ai_lakehouse_facilities_star_schema.sql)
   - [sql/create_ai_lakehouse_dimensional_gold_schema.sql](sql/create_ai_lakehouse_dimensional_gold_schema.sql)

## AIDP Setup Order

The workshop now follows Oracle's AIDP quick-start flow, contextualized for the MPHA healthcare use case:

1. Provision or reuse the AIDP instance
2. Assign user access with AIDP roles
3. Create or confirm the shared AIDP workspace `E2EAIDPIndustryDemos`
4. Create or confirm the Spark compute `E2EAIDPIndustrydemos`
5. Create the standard Object Storage-backed catalog `e2eindustrydemos.default`
6. Create external volume `e2eindustrydemovol` mapped to the Object Storage `mpha` prefix
7. Create the external Autonomous AI Lakehouse catalog `goldailh`
8. Create participant AI Lakehouse schemas such as `MPHA_P01` through `MPHA_P17`, apply quota, create Claims star schema tables, grant `E2EAIDPUSER`, and refresh the external catalog
9. Organize participant notebook folders under `Participants/<participant_id>`
10. Run the medallion notebooks in order

See [workshop_guide.md](workshop_guide.md) for the full step-by-step walkthrough and workshop-specific naming guidance.

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
- Two Gold star paths designed for AI Lakehouse and OAC
- An instructor-led Claims star schema workbook plus a participant-owned Facility Access dashboard challenge
- Interactive dashboard mockups, spatial insight examples, and vector-chat patterns
- Optional extension labs for machine learning and a Claims and Policy Copilot

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

- Publish dimensional stars in Autonomous AI Lakehouse
- Reuse the same Silver foundation for two different Gold teaching paths
- Support instructor-led claims analytics first, then participant-led facility-access modeling

The recommended Gold layer now branches into:

- `mpha_fact_claims_monthly` plus `mpha_dim_date`, `mpha_dim_district`, `mpha_dim_coverage_program`, and `mpha_dim_claim_type`
- `mpha_fact_facility_access_daily` plus `mpha_dim_date`, `mpha_dim_facility`, `mpha_dim_district`, and `mpha_dim_pressure_band`

The Claims star schema is the provided OAC reference workbook. The Facility Access Daily star schema is intentionally left as the participant challenge so the same design pattern has to be applied independently.

Reference material:

- [medallion_architecture.md](medallion_architecture.md)
- [sql/create_ai_lakehouse_claims_star_schema.sql](sql/create_ai_lakehouse_claims_star_schema.sql)
- [sql/create_ai_lakehouse_facilities_star_schema.sql](sql/create_ai_lakehouse_facilities_star_schema.sql)
- [sql/create_ai_lakehouse_dimensional_gold_schema.sql](sql/create_ai_lakehouse_dimensional_gold_schema.sql)
- [data/gold_dimensional/](data/gold_dimensional/)

## Dashboard And Insight Coverage

The OAC wireframes and workshop narrative now focus on:

- The instructor-led Claims star schema workbook
- Claims, disbursement, and program funding monitoring
- Interactive filters, metrics, and grounded assistant prompts for the claims story
- Spatial and document-chat assets as adjacent workshop capabilities
- A participant extension path for Facility Access Daily dashboard creation

Useful references:

- [dashboard_spec.md](dashboard_spec.md)
- [OAC Executive Overview build guide](lab4_oac_executive_overview_build_guide.html)
- [assets/oac_dashboard_lab/screenshots/42_oac_live_consumer_assistant_denied_claims_additional_insights.png](assets/oac_dashboard_lab/screenshots/42_oac_live_consumer_assistant_denied_claims_additional_insights.png)
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
  Produces optional broader Gold-stage compatibility outputs and business-serving views.

- [notebooks/aidp_claims_star_ai_lakehouse_pyspark.py](notebooks/aidp_claims_star_ai_lakehouse_pyspark.py)  
  Loads the instructor-led Claims star schema directly into each participant's assigned Autonomous AI Lakehouse schema, such as `goldailh.MPHA_P17`.

Recommended notebook path for the instructor-led Claims workshop:

- Run `notebooks/aidp_bronze_pyspark.py`
- Run `notebooks/aidp_silver_pyspark.py`
- Run `notebooks/aidp_claims_star_ai_lakehouse_pyspark.py` to write directly into the connected Autonomous AI Lakehouse catalog and assigned participant schema
- Use `notebooks/aidp_gold_pyspark.py` only as the optional staged-file path

Use [workflows/aidp_incremental_medallion_workflow.md](workflows/aidp_incremental_medallion_workflow.md) to create the validated AIDP Workflow that orchestrates Bronze, Silver, Gold staging, and AI Lakehouse load tasks. Set a 60-minute timeout on each task. The AI Lakehouse load notebook uses a key-based left-anti join so repeated workflow runs insert only new Claims star schema rows.

- [notebooks/aidp_ml_claims_denial_risk_pyspark.py](notebooks/aidp_ml_claims_denial_risk_pyspark.py)  
  Optional ML notebook that trains and publishes claims denial risk scores from curated Gold inputs.

- [notebooks/aidp_refinement_pyspark.py](notebooks/aidp_refinement_pyspark.py)  
  Retained as a single-script reference version of the medallion flow.

## Repository Map

- [index.html](index.html) - shareable workshop landing page
- [workshop_single_flow.html](workshop_single_flow.html) - combined end-to-end lab flow for facilitation
- [workshop_guide.md](workshop_guide.md) - detailed facilitator guide
- [workshop_guide.pdf](workshop_guide.pdf) - downloadable formatted guide
- [data_dictionary.md](data_dictionary.md) - business definitions and column details
- [manifest.json](manifest.json) - generated artifact manifest
- [workflows/](workflows/) - AIDP workflow runbook and reference task graph
- [optional_labs/](optional_labs/) - machine learning and agent extension labs
- [github_migration.md](github_migration.md) - repository handoff instructions

## Optional Labs

- [optional_labs/claims_denial_risk_scoring.md](optional_labs/claims_denial_risk_scoring.md)
- [optional_labs/claims_policy_copilot_agent.md](optional_labs/claims_policy_copilot_agent.md)

These labs extend the core workshop into:

- Claims denial risk scoring using curated claims, event, and accreditation context
- A Claims and Policy Copilot using SQL over the Gold layer plus RAG over the policy playbook

## Data Privacy

All data in this repository is synthetic and intended for workshop use only. It contains no real patient names, precise addresses, medical record numbers, or protected health information.

## GitHub Handoff

If this kit is being copied, rebranded, or moved into another repository, use [github_migration.md](github_migration.md) for the handoff steps.
