# Public Healthcare AIDP Workshop

## About This Workshop

Public healthcare organizations need to balance service access, clinical capacity, staffing, immunization campaigns, claims adjudication, public-program disbursement, membership eligibility, provider accreditation, and emerging public-health risks. In this workshop, you will build a lakehouse analytics pipeline for Metro Public Health Authority (MPHA), a fictional public healthcare network serving five districts through hospitals, urgent-care centers, and community clinics.

You will load synthetic healthcare operations data, refine it through a medallion architecture using Spark and Delta Lake in Oracle AI Data Platform, and serve the Gold business layer through dimensional stars in Autonomous AI Lakehouse. The workshop then branches into two outcomes: an instructor-led Claims star schema with a guided OAC workbook, and a participant-built Facility Access Daily star schema used to test whether participants can model and visualize the same pattern on their own.

## Business Use Case

MPHA leadership wants a daily and weekly decision-support view that answers:

- Which facilities are exceeding wait-time or occupancy targets?
- Which districts have the highest access risk?
- Are immunization campaigns reaching older residents and high-need districts?
- Is respiratory illness pressure creating emergency department strain?
- Which service-quality issues are growing and how quickly are they being resolved?
- Which claim types or programs have rising denial rates or payment leakage?
- Are public healthcare disbursements timely, paid, and traceable by funding source?
- Which membership segments need eligibility renewal or high-risk care management?
- Which providers have accreditation gaps, corrective actions, or expiry risk?
- Where should leaders prioritize staffing, clinic sessions, outreach, and capacity relief?

## Workshop Info

**Length:** 3 hours for core labs; optional extensions add 45 to 60 minutes each.

**Services used:**

- Oracle Object Storage
- Oracle AI Data Platform with Spark and Delta Lake
- Autonomous AI Data Lakehouse or Autonomous Data Warehouse
- Oracle Analytics Cloud
- Optional: OCI Generative AI Agents

**Dataset period:** January 1, 2025 to June 30, 2025

**Dataset type:** Five synthetic CSV datasets, one JSONL event dataset, one GeoJSON spatial dataset, and one synthetic operating playbook document

## Recommended Execution Flow

Use `workshop_single_flow.html` as the main facilitator and participant runbook. It combines environment setup, AIDP medallion processing, Claims star schema publishing, OAC dashboarding, the Facility Access Daily challenge, and optional ML and agent extensions into one end-to-end path.

Use the detailed lab pages and this guide as drill-down references when a participant needs screenshots, SQL details, validation checks, or troubleshooting notes.

## Architecture

1. Raw CSV, JSONL, GeoJSON, and document files are uploaded to object storage as the immutable landing zone.
2. AI Data Platform creates the **Bronze** layer as schema-preserving Delta tables with ingestion metadata.
3. AI Data Platform creates the **Silver** layer as conformed Delta tables with typed fields, quality rules, reference joins, spatial feature extraction, document chunk metadata, and derived operational flags.
4. Autonomous AI Lakehouse hosts the **Gold** layer as two teaching paths: an instructor-led Claims star schema and a DIY Facility Access Daily star schema, both built from the shared Silver foundation.
5. OAC connects only to the Claims star schema during the guided dashboard lab; participants design their own Facility Access Daily dashboard afterward as the hands-on challenge.

## Workshop Role Convention

To keep execution responsibilities clear during the workshop:

- **Admin step** means the facilitator, environment owner, or platform administrator performs the action once for the shared workshop environment.
- **Participant step** means each participant or team performs the action in their own hands-on flow.

### Who Does What

**Admin / facilitator responsibilities**

- provision shared AIDP, AI Lakehouse, and OAC resources
- create shared users, connections, catalogs, and datasets
- preload any assets or datasets that should not be repeated by every participant
- enable assistant, governance, or optional shared services where needed

**Participant responsibilities**

- sign in to the prepared environment
- run notebooks and validate outputs
- load or validate their own workshop data where requested
- build workbook content and complete guided or DIY exercises
- test optional ML and agent labs when included

## Lab 1 - Create a Healthcare Lakehouse with AI Data Platform

### Objectives

- Provision or identify the Oracle AI Data Platform environment for the workshop.
- Create the workspace, Spark cluster, and catalogs needed for the healthcare flow.
- Create or identify an object storage bucket for workshop data.
- Upload the raw MPHA CSV files.
- Create a Spark notebook in AI Data Platform.
- Read and profile the raw files.

### Files to upload

Upload these five CSV files from `data/raw/`:

- `district_health_profile.csv`
- `facility_provider_master.csv`
- `facility_operations_daily.csv`
- `population_health_weekly.csv`
- `claims_membership_disbursement.csv`

Upload these additional source files:

- `data/raw_json/facility_capacity_events.jsonl`
- `data/raw_spatial/healthcare_service_areas.geojson`
- `documents/MPHA_Winter_Respiratory_Response_Playbook.docx`

### Admin Steps

Participants: you can skip this section and join once the facilitator confirms the shared environment is ready.

The setup sequence below is intentionally aligned to the six AIDP quick-start sections from Oracle, with healthcare-specific workshop inputs added where needed.

1. Section 1 - AIDP Provisioning
   - Open `Analytics & AI`, then `AI Data Platform`.
   - Click `Create AI Data Platform` if the shared workshop environment does not already exist.
   - Enter a workshop-friendly instance name such as `mpha-aidp`.
   - Enter a default workspace name such as `mpha-workshop-ws`.
   - Choose `Standard` for simpler workshop setup, or `Advanced` if your tenancy requires finer policy control.
   - Copy the generated IAM policy statements and apply them in the correct tenancy or compartment.
   - Return to the provisioning page and click `Create`.
   - Open the newly provisioned AI Data Platform instance after status becomes available.
2. Section 2 - User Access Management
   - Open `Roles`.
   - Choose the required admin role for facilitators, such as the AI Data Platform admin or workspace-admin role.
   - Open `Members` and add the facilitator accounts.
   - Repeat for participant-facing roles that allow notebook use, workspace access, and catalog usage.
   - Validate that a facilitator can see the workspace, catalogs, and compute choices.
3. Section 3 - Workspace and Cluster Setup
   - Open `Workspaces` and click `Create` if you are not using the default workspace.
   - Use a name such as `mpha-core-workshop`.
   - Set the default catalog to the shared standard catalog that will hold the healthcare landing volumes.
   - Open `Compute` and click `Create`.
   - Use a cluster name such as `mpha-spark-cluster`.
   - Select the `Spark` runtime.
   - If available, start with `Quickstart`.
   - Size the driver and workers for workshop execution rather than production-scale tuning.
   - Enable autoscaling if your team prefers elastic usage.
4. Section 4 - Catalog Setup with OCI Object Storage
   - Open the OCI Console navigation menu and go to `Storage -> Buckets`.
   - Select the compartment where the workshop bucket should live.
   - Click `Create Bucket`.
   - Enter a bucket name such as `mpha-workshop-bucket`.
   - Keep the default storage tier unless your tenancy requires a different choice.
   - Click `Create`.
   - Open the new bucket.
   - Create the workshop folder structure so each AIDP volume can point to a clean path:
     - `mpha/raw/`
     - `mpha/raw_json/`
     - `mpha/raw_spatial/`
     - `mpha/documents/`
     - `mpha/bronze/`
     - `mpha/silver/`
     - `mpha/gold_stage/`
     - `mpha/gold_dimensional/`
     - `mpha/vector/`
   - If your Object Storage view does not show a dedicated folder-create action, upload a small placeholder file into each prefix or use the `Create folder` action if available in your tenancy UI.
   - Confirm that the bucket and prefixes are visible before you move into catalog and volume creation.
   - Open `Master Catalog`.
   - Create a standard catalog such as `MPHA_WORKSHOP_CAT`.
   - Create a schema such as `mpha_landing`.
   - In the `mpha_landing` schema, open the `Volume` tab and create external volumes for:
     - `mpha/raw/`
     - `mpha/raw_json/`
     - `mpha/raw_spatial/`
     - `mpha/documents/`
     - `mpha/bronze/`
     - `mpha/silver/`
     - `mpha/gold_stage/`
     - `mpha/gold_dimensional/`
     - `mpha/vector/`
   - For each volume, choose `External` and point it to the correct compartment, bucket, and folder.
5. Section 5 - Catalog Setup with Oracle Autonomous AI Lakehouse
   - In `Master Catalog`, click `Create Catalog`.
   - Set `Catalog Type` to `External`.
   - Choose the connection type for Autonomous AI Lakehouse.
   - Use either wallet-based access or direct instance-based connectivity, depending on your environment.
   - Test and save the catalog with a name such as `MPHA_AILH_CAT`.
   - Open the matching Gold-serving schema in the external catalog and confirm the star schema tables will be visible there once loaded.
6. Section 6 - Notebook Management
   - Open the shared workspace folder structure.
   - Create folders such as `01_bronze`, `02_silver`, `03_gold`, `04_ml`, `05_agent`, and `shared_assets`.
   - Upload or create the starter notebooks:
     - `aidp_bronze_pyspark.py`
     - `aidp_silver_pyspark.py`
     - `aidp_gold_pyspark.py`
     - `aidp_claims_star_ai_lakehouse_pyspark.py`
   - Open a notebook and attach the shared Spark cluster so the execution environment is ready for participants.

### Participant Steps

1. Sign in to the workshop workspace and confirm that you can see the shared folders, catalogs, and Spark cluster.
2. Upload the raw datasets if the facilitator has not preloaded them.
   - Create or verify the object storage folders:
     - `mpha/raw/`
     - `mpha/raw_json/`
     - `mpha/raw_spatial/`
     - `mpha/documents/`
   - Upload the five CSV files, one JSONL file, one GeoJSON file, and one DOCX file.
3. Open the Bronze notebook in the `01_bronze` folder and attach the shared Spark cluster.
4. Use `notebooks/aidp_bronze_pyspark.py` as the starter notebook and set:
   - `raw_base`
   - `raw_json_base`
   - `raw_spatial_base`
   - `document_base`
   - `bronze_base`
5. Read each raw source and confirm the row counts match `manifest.json`.

### Expected Outcome

You have an AIDP environment that is ready for the workshop: workspace, cluster, catalogs, volumes, uploaded healthcare sources, and a connected Bronze notebook.

Reference blog for the Lab 1 setup pattern:

- [Continuing Your Oracle AI Data Platform Journey: Quick Start Guide](https://blogs.oracle.com/ai-data-platform/continuing-your-oracle-ai-data-platform-journey-quick-start-guide)

## Lab 2 - Build Bronze and Silver Layers with AI Data Platform

### Objectives

- Convert raw CSV files into Bronze Delta tables without changing source values.
- Add ingestion metadata such as source file, batch id, and load timestamp.
- Create Silver Delta tables with clean, typed, conformed healthcare data.
- Add derived measures for access risk, wait-time variance, high occupancy, immunization completion, public-health pressure, triage totals, and capacity pressure bands.
- Extract spatial features from GeoJSON and prepare a spatial access insight.
- Prepare playbook document chunks for vector search and grounded chat.

### Admin Notes

Participants: you can ignore this unless the facilitator asks you to use the legacy combined notebook.

1. Keep `notebooks/aidp_refinement_pyspark.py` only as a legacy combined reference if a facilitator wants one file instead of the split flow.

### Participant Steps

1. Run `notebooks/aidp_bronze_pyspark.py` to write raw-preserving Bronze Delta tables.
2. Run `notebooks/aidp_silver_pyspark.py` to type, validate, and conform the healthcare data into Silver Delta tables.
3. For the instructor-led Claims path, run `notebooks/aidp_claims_star_ai_lakehouse_pyspark.py` to build the Claims star schema dimensions and fact directly in the connected Autonomous AI Lakehouse external catalog.
4. Use `notebooks/aidp_gold_pyspark.py` only when the facilitator wants the broader flat Gold-serving compatibility outputs staged to object storage.

### AIDP Workflow Pattern for Incremental Medallion Runs

After participants run the notebooks manually, the facilitator should create or review the validated AIDP Workflow version of the same sequence. This keeps the hands-on path simple while introducing how data-engineering notebooks become an operational pipeline.

Use `workflows/aidp_incremental_medallion_workflow.md` as the workflow runbook.

Recommended workflow name:

`MPHA_INCREMENTAL_MEDALLION_FLOW`

Validated workflow settings:

| Setting | Validated value |
| --- | --- |
| Workspace | `E2EAIDPIndustryDemos` |
| Compute | `E2EAIDPIndustrydemos` |
| Timeout per task | `30` minutes in the validated run; increase if your compute startup is slower |
| Bronze task | Python task in the validated run |
| Silver, Gold, AI Lakehouse tasks | Notebook tasks |

Important: set a timeout value on each task before adding the next downstream task.

Workflow parameters to explain:

| Parameter | Purpose |
| --- | --- |
| `run_mode` | `FULL_REFRESH` for the first classroom run, `INCREMENTAL` for the operational rerun discussion. |
| `batch_id` | Labels the raw-data load and supports replay and audit. |
| `watermark_start` | Lower bound for the incremental source window. |
| `watermark_end` | Upper bound for the incremental source window. |
| `target_catalog` | AIDP external AI Lakehouse catalog, such as `goldailh`. |
| `target_schema` | Participant Gold schema, such as `e2eaidpuser`. |

Workflow task sequence:

| Task | Validated asset | Dependency | Incremental concept |
| --- | --- | --- | --- |
| `bronzeingest` | `/Workspace/O1_Bronze/aidp_bronze_pyspark.py` | None | Append or deduplicate new raw records by batch id and source file. |
| `silverrefine` | `/Workspace/O2_Silver/02_silver.ipynb` | `bronzeingest` | Recompute impacted Silver records or partitions. |
| `goldstage` | `/Workspace/03_Gold/03_Gold.ipynb` | `silverrefine` | Stage broader Gold compatibility outputs when needed. |
| `lakehouseload` | `/Workspace/03a_GoldAILHLoad/03a_GoldAILHLoad.ipynb` | `goldstage` | Insert only new Claims star schema dimension and fact rows into AI Lakehouse. |
| Claims validation | `sql/claims_star_validation.sql` | `lakehouseload` | Block OAC, ML, and agent use until validation passes. |

Instructor talk track:

1. The first run is a clear full-refresh workshop execution.
2. The second run is the incremental story: new batch id, new watermark window, impacted Bronze/Silver/Gold processing, and validation gates.
3. The AI Lakehouse connector did not support destructive table reset operations from Spark during validation, so the load notebook now reads existing target keys and inserts only new rows.
4. If a downstream task fails, use **Repair run** and select only the failed task after correcting the notebook.
5. In production, extend the same idea into parameter cells, Delta append or merge logic, partition-aware Silver processing, AI Lakehouse dimension upserts, and fact-grain refresh logic.

### Bronze Layer in AIDP

Bronze is the repeatable raw-data layer. It preserves the workshop source data and adds only technical ingestion metadata.

| Bronze table | Source file | Grain | Bronze logic |
| --- | --- | --- | --- |
| `bronze_district_health_profile` | `district_health_profile.csv` | District | Preserve district population, need, and health-context attributes. |
| `bronze_facility_provider_master` | `facility_provider_master.csv` | Facility/provider | Preserve facility master data plus provider accreditation fields. |
| `bronze_facility_operations_daily` | `facility_operations_daily.csv` | Facility-day | Preserve daily operations, access, staffing, satisfaction, and daily quality-event measures. |
| `bronze_population_health_weekly` | `population_health_weekly.csv` | District-week-age group | Preserve immunization and respiratory surveillance measures in one weekly population-health source. |
| `bronze_claims_membership_disbursement` | `claims_membership_disbursement.csv` | Claim transaction | Preserve synthetic claim, member segment, eligibility, program, disbursement, and payment fields. |
| `bronze_facility_capacity_events` | `facility_capacity_events.jsonl` | Facility-event | Preserve nested JSON capacity-event payloads and add ingestion metadata. |
| `bronze_healthcare_service_areas_geojson` | `healthcare_service_areas.geojson` | GeoJSON FeatureCollection | Preserve district boundary, facility point, and facility catchment features in one spatial source. |
| Document source | `MPHA_Winter_Respiratory_Response_Playbook.docx` | Document | Use AIDP/document tooling to chunk and vectorize the single playbook document. |

### Silver Layer in AIDP

Silver is the conformed analytics layer. It applies business quality rules while remaining detailed enough for reuse.

| Silver table | Grain | Silver logic |
| --- | --- | --- |
| `silver_district` | District | Type district profile fields and deduplicate district keys. |
| `silver_facility_provider` | Facility/provider | Join facility-provider master to district profile; standardize facility type and accreditation status. |
| `silver_facility_day` | Facility-day | Parse `service_date`, validate volumes/rates, calculate wait variance, high-occupancy flag, access risk, and quality-event measures. |
| `silver_population_health_week` | District-week-age group | Parse `week_start_date`, validate campaign and surveillance measures, calculate completion and no-show rates. |
| `silver_district_health_week` | District-week | Aggregate population-health rows to district-week and calculate public-health pressure index. |
| `silver_claims_membership_disbursement` | Claim transaction | Parse claim, eligibility, renewal, and disbursement dates; validate amounts; standardize claim and payment status. |
| `silver_provider_accreditation` | Provider accreditation record | Derived from `silver_facility_provider` for provider oversight and accreditation-risk facts. |
| `silver_facility_capacity_event` | Facility-event | Parse event timestamp, type nested JSON triage fields, calculate triage total, supply-alert count, and pressure band. |
| `silver_spatial_feature` | Spatial feature | Explode the single GeoJSON file and classify district, facility, and catchment features by `source_layer`. |
| `silver_playbook_chunk` | Document chunk | Created from the single DOCX playbook during the document-vector step. |

### Shared Bronze-to-Silver teaching pattern

Use the Bronze-to-Silver flow as the common modeling foundation before the workshop branches:

- `bronze_claims_membership_disbursement -> silver_claims_membership_disbursement`
  - Parse `service_date`, `eligibility_start_date`, `eligibility_end_date`, `renewal_due_date`, and `disbursement_date`
  - Cast financial fields to numeric types
  - Standardize claim, payment, and eligibility status values
- `bronze_facility_operations_daily + silver_facility_provider -> silver_facility_day`
  - Derive `ed_wait_variance_minutes`
  - Derive `outpatient_wait_variance_minutes`
  - Derive `high_occupancy_flag`
  - Derive `access_risk_score`
- `bronze_population_health_weekly -> silver_population_health_week`
  - Derive `completion_rate`
  - Derive `immunization_no_show_rate`
- `silver_population_health_week + silver_district -> silver_district_health_week`
  - Aggregate to district-week
  - Derive `public_health_pressure_index`
- `bronze_facility_capacity_events -> silver_facility_capacity_event`
  - Derive `triage_total`
  - Derive `supply_alert_count`
  - Derive `capacity_pressure_band`
- `bronze_healthcare_service_areas_geojson -> silver_spatial_feature`
  - Explode features
  - Classify `source_layer`
- `MPHA_Winter_Respiratory_Response_Playbook.docx -> silver_playbook_chunk`
  - Derive `document_id`, `chunk_id`, `page_number`, `section_title`, `embedding_model`, and `embedding_json`

### Gold Layer in Autonomous AI Lakehouse

Gold is the business serving layer. The recommended model is a dimensional star in Autonomous AI Lakehouse so OAC connects to shared, reusable dimensions and facts rather than notebook outputs or isolated flat files.

The package also includes flat Gold mart samples in `data/gold/` for quick validation, but the workshop execution path should use `data/gold_dimensional/` together with the split AI Lakehouse SQL scripts:

- `sql/create_ai_lakehouse_claims_star_schema.sql` for the instructor-led Claims star schema
- `sql/create_ai_lakehouse_facilities_star_schema.sql` for the Facility Access Daily and facilities/public-health path
- `sql/create_ai_lakehouse_dimensional_gold_schema.sql` only when the facilitator wants the combined all-in-one script

### Gold branch used in the workshop

After Silver, the workshop branches into two Gold options:

1. **Instructor-led path: Claims star schema**
   - Silver source: `silver_claims_membership_disbursement`
   - Gold fact: `mpha_fact_claims_monthly`
   - Gold dimensions: `mpha_dim_date`, `mpha_dim_district`, `mpha_dim_coverage_program`, `mpha_dim_claim_type`
   - Gold derivations:
     - aggregate claim rows to service month, district, program, and claim type
     - derive `claims_submitted`, `approved_claims`, `denied_claims`, and `pending_claims`
     - derive `total_submitted_amount`, `total_approved_amount`, and `total_paid_amount`
     - derive `avg_processing_days`
     - derive `denial_rate`
   - OAC outcome: instructor builds the provided Claims star schema workbook

2. **DIY path: Facility Access Daily star schema**
   - Silver sources: `silver_facility_day`, `silver_facility_provider`
   - Gold fact: `mpha_fact_facility_access_daily`
   - Gold dimensions: `mpha_dim_date`, `mpha_dim_facility`, `mpha_dim_district`, `mpha_dim_pressure_band`
   - Gold derivations:
     - publish facility-day operational measures
     - derive or assign `pressure_band_key`
     - retain `district_key` in the fact so OAC joins directly to district and facility dimensions
   - OAC outcome: participants design their own Facility Access Daily dashboard as the challenge exercise

### Gold Dimensions

| Dimension | Grain | Purpose |
| --- | --- | --- |
| `mpha_dim_date` | Date | Shared service date, week start, month, quarter, and year attributes. |
| `mpha_dim_district` | District | District population, deprivation, elderly share, chronic-condition share, and income context. |
| `mpha_dim_facility` | Facility | Facility master data, district identifiers, coordinates, licensed beds, and wait targets. |
| `mpha_dim_age_group` | Age band | Immunization age-group sorting and labels. |
| `mpha_dim_quality_event` | Event type and severity | Conformed quality event category and severity attributes. |
| `mpha_dim_pressure_band` | Pressure band | Watch, Medium, and High operating bands reused by multiple facts. |
| `mpha_dim_document_chunk` | Document chunk | Playbook chunk text, page, section, and embedding metadata. |
| `mpha_dim_coverage_program` | Coverage program | Public healthcare program, program type, and funding source. |
| `mpha_dim_claim_type` | Claim type | Claim type, service category, and coarse diagnosis group. |
| `mpha_dim_member_segment` | Member segment | Age group, risk segment, and chronic-condition flag. |
| `mpha_dim_accreditation_status` | Accreditation status | Accreditation body, status, level, and provider specialty scope. |

### Gold Facts

| Fact | Grain | Main dimensions | Business purpose |
| --- | --- | --- | --- |
| `mpha_fact_facility_access_daily` | Facility-day | Date, Facility, District, Pressure Band | Daily access, wait, capacity, staffing, satisfaction, and access risk. |
| `mpha_fact_district_public_health_weekly` | District-week | Date, District, Pressure Band | Public-health pressure, immunization completion, no-show, positivity, and respiratory ED demand. |
| `mpha_fact_immunization_equity_weekly` | District-week-age group | Date, District, Age Group | Campaign reach and equity analysis by district and age group. |
| `mpha_fact_quality_event_summary` | Facility-event type-severity | Facility, District, Quality Event | Service-quality volume, closure time, SLA breach, and readmission indicators. |
| `mpha_fact_spatial_access_insight` | District | District, Pressure Band | Residents per facility, distance, pressure, and mobile-clinic planning recommendations. |
| `mpha_fact_capacity_event` | Facility-event | Date, Facility, District, Pressure Band | JSON capacity-event signals for real-time operations views. |
| `mpha_bridge_chat_topic_chunk` | Question-chunk | Document Chunk | Bridge table linking chat prompts to retrieved playbook chunks. |
| `mpha_fact_claims_monthly` | District-month-program-claim type | Date, District, Coverage Program, Claim Type | Claims volume, approval, denial, pending, payment yield, and processing time. |
| `mpha_fact_disbursement_monthly` | District-month-program-payee type | Date, District, Coverage Program | Public-program disbursement count, amount, pending, failed, and payment-cycle metrics. |
| `mpha_fact_membership_snapshot` | District-program-member segment snapshot | Date, District, Coverage Program, Member Segment | Membership, active eligibility, renewals due, suspended members, and high-risk members. |
| `mpha_fact_provider_accreditation` | Facility-provider accreditation snapshot | Date, Facility, District, Accreditation Status, Pressure Band | Accreditation score, corrective actions, days to expiry, and accreditation risk band. |
| `mpha_gold_claims_denial_risk_scores` | District-month-program-claim type score | Date, District, Coverage Program, Claim Type | Optional ML scoring output that prioritizes likely denial hotspots for manual review. |

This is a star schema because the fact tables carry the foreign keys needed for analysis directly. Facility-grain facts join straight to both `mpha_dim_facility` and `mpha_dim_district`, while district-grain facts join directly to `mpha_dim_district`.

| Flat compatibility object | Grain | Business purpose |
| --- | --- | --- |
| `gold_facility_access_daily` | Facility-day | Daily access, wait-time, occupancy, staffing, and satisfaction KPIs. |
| `gold_district_public_health_weekly` | District-week | Public-health pressure, immunization completion, no-show, positivity, and respiratory ED pressure. |
| `gold_immunization_equity_weekly` | District-week-age group | Campaign reach and equity analysis by district and age group. |
| `gold_quality_event_summary` | Facility-severity-event type | Service-quality volume, closure time, SLA breach, and avoidable readmission indicators. |
| `gold_executive_overview` | Reporting period | OAC-ready executive summary metrics and risk indicators. |
| `gold_spatial_access_insights` | District | Residents per facility, average distance, pressure, and mobile-clinic planning recommendations. |
| `gold_capacity_event_latest` | Facility-event | Near-real-time capacity signals from JSON events for the OAC real-time dashboard tab. |
| `gold_document_chat_context` | Document chunk | Vector-search context for grounded chat with data and documents. |
| `gold_claims_summary` | District-month-program-claim type | Claims adjudication, denial, approval, payment amount, and processing-time summary. |
| `gold_disbursement_summary` | District-month-program-payee type | Disbursement amount, payment status, funding source, and cycle-time summary. |
| `gold_membership_summary` | District-program-member segment snapshot | Eligibility, renewal, risk-segment, and chronic-condition membership summary. |
| `gold_provider_accreditation_summary` | Facility-provider accreditation snapshot | Accreditation score, corrective actions, expiry timing, and accreditation risk summary. |

### Suggested Transformations

- Parse `service_date`, `event_date`, and `week_start_date` as dates.
- Join facilities to community indicators by `district_id`.
- Calculate wait-time variance against facility targets.
- Flag high occupancy when `bed_occupancy_rate >= 0.90`.
- Calculate immunization completion and no-show rates.
- Combine respiratory surveillance with immunization activity by district and week.
- Calculate `public_health_pressure_index` as a composite indicator for leadership triage.
- Explode the single GeoJSON `features` array into Silver spatial features and classify rows by `source_layer`.
- Calculate `residents_per_facility` and spatial action recommendations for mobile clinic planning.
- Chunk and vectorize the single MPHA playbook document for grounded chat.
- Normalize claims by program, claim type, service category, and coarse diagnosis group; calculate denial rate, payment yield, and processing time.
- Normalize disbursements by funding source and payee type; calculate pending, failed, paid, and cycle-time metrics.
- Normalize membership by program, age group, risk segment, chronic-condition flag, and renewal status.
- Normalize provider accreditation by facility, body, status, level, score, corrective actions, and expiry risk.
- Build or stage dimensional Gold outputs under `data/gold_dimensional/`.
- Load the dimensional Gold schema in Autonomous AI Lakehouse using the split SQL files for the relevant path:
  - `sql/create_ai_lakehouse_claims_star_schema.sql`
  - `sql/create_ai_lakehouse_facilities_star_schema.sql`
  - keep `sql/create_ai_lakehouse_dimensional_gold_schema.sql` as the combined fallback script
- Use `sql/create_ai_lakehouse_gold_layer.sql` only if a facilitator wants the simpler flat-mart path for comparison.

### Expected Outcome

You have Bronze and Silver Delta layers in AI Data Platform and a dimensional Gold serving layer in Autonomous AI Lakehouse, including spatial planning, real-time event, and document-chat serving objects.

## Lab 3 - Publish Claims star schema to Autonomous AI Lakehouse

### Objectives

- Confirm the Autonomous AI Lakehouse target schema and workshop users.
- Load the instructor-led Claims star schema from AIDP into the connected AI Lakehouse external catalog.
- Validate the Claims star schema tables before opening OAC.
- Prepare a clean handoff into the OAC Executive Overview lab.

### Admin Steps

Participants: you can skip this section and join once the facilitator confirms that the shared Lakehouse and OAC setup is ready.

1. Create or confirm the shared Autonomous AI Lakehouse instance.
   - In OCI, open `Oracle AI Database`, then `Autonomous AI Database`.
   - Click `Create Autonomous AI Database` if the workshop Lakehouse instance does not already exist.
   - Enter the display name and database name for the shared workshop instance.
   - Choose the workload type `Lakehouse`.
   - Select the database version, ECPU size, storage, and network access settings required for the workshop.
   - Wait until the instance shows as available before continuing.
2. Create the workshop users in the Autonomous AI Lakehouse UI before participants begin SQL validation or OAC connectivity checks.
   - Open the target `Autonomous AI Lakehouse` instance and launch `Database Actions`.
   - Sign in as `ADMIN`.
   - Open the left navigation, then go to `Administration -> Database Users`.
   - Click `+ Create User`.
   - Create the shared Gold-serving owner such as `MPHA_GOLD_OWNER` and the participant or team users such as `MPHA_P01`, `MPHA_P02`, or `MPHA_TEAM1`.
   - Assign strong temporary passwords and enable `Web Access`.
   - Set `Quota on tablespace DATA`:
     - participant quota: `1G`
     - facilitator or shared schema quota: `2G` to `5G`
   - Open the `Granted Roles` tab and grant `DWROLE`, plus `CONNECT` if your tenancy standard still expects it.
   - Confirm the users are `REST Enabled`.
   - Set quota on tablespace `DATA` high enough for workshop loading. For the direct AIDP Claims star schema notebook path, `1G` is a practical minimum; use `2G` to `5G` for facilitator or shared schemas when you want more headroom.
   - Copy the Database Actions URL from the user card and share it with the participant together with the username and temporary password.
3. Create the Claims star schema target tables in the Gold-serving schema.
   - Use `sql/create_ai_lakehouse_claims_star_schema.sql` for the instructor-led Claims path.
   - Use a schema such as `MPHA_GOLD_OWNER` or the assigned participant/team schema.
   - Confirm these tables exist before participants run the direct-load notebook:
     - `mpha_dim_date`
     - `mpha_dim_district`
     - `mpha_dim_coverage_program`
     - `mpha_dim_claim_type`
     - `mpha_fact_claims_monthly`
4. Confirm the AIDP external catalog can see the target AI Lakehouse schema.
5. Share the target catalog and schema names with participants before the notebook execution step.

### Participant Steps

1. Sign in to Database Actions with the assigned workshop user and run `select user from dual;` in `SQL` to confirm that you land in the expected schema.
2. Run `notebooks/aidp_claims_star_ai_lakehouse_pyspark.py` after the Silver notebook completes.
3. Set the notebook variables for:
   - `silver_base`
   - `target_catalog`
   - `target_schema`
4. Use the connected external Autonomous AI Lakehouse catalog, such as `MPHA_AILH_CAT`, and the assigned Gold-serving schema, such as `MPHA_GOLD_OWNER`.
5. Confirm these prerequisites before running the write step:
   - the target schema exists in the external catalog
   - the target tables already exist in Autonomous AI Lakehouse
   - the target user has quota on tablespace `DATA`
6. The notebook writes with `insertInto()` into existing AI Lakehouse tables, so treat it as the direct-load path for an already prepared Claims star schema.
7. Confirm that the notebook writes these instructor-led Claims star schema tables:
   - `mpha_dim_date`
   - `mpha_dim_district`
   - `mpha_dim_coverage_program`
   - `mpha_dim_claim_type`
   - `mpha_fact_claims_monthly`
8. Run the validation SQL pack in Database Actions.
9. Confirm all five Claims star schema tables return non-zero row counts.
10. Confirm the orphan-row check returns `0`.
11. Confirm the joined preview query returns readable district, program, claim type, and claims measures.
12. Continue to Lab 4 after the Claims star schema is validated.

Quick validation pack:

- Run `sql/claims_star_validation.sql` in Database Actions after the notebook completes.
- Expected outcomes:
  - all five Claims star schema tables return non-zero row counts
  - orphan-row check returns `0`
  - joined preview returns readable business rows with populated claims measures

Alternative loading path:

- If the facilitator prefers a SQL-driven load instead of the direct AIDP catalog write, use `notebooks/aidp_gold_pyspark.py` to stage outputs and then run `sql/create_ai_lakehouse_dimensional_gold_schema.sql` in Database Actions.
- To avoid workshop confusion, prefer:
  - `sql/create_ai_lakehouse_claims_star_schema.sql` for the instructor-led Claims path
  - `sql/create_ai_lakehouse_facilities_star_schema.sql` for the Facility Access Daily path

Recommended workshop pattern:

- keep one shared Gold-serving owner such as `MPHA_GOLD_OWNER` for loading the Claims star schema, Facility Access Daily star schema, and the OAC-facing views
- create separate participant users such as `MPHA_P01` to `MPHA_P20` for hands-on SQL checks and learning exercises

Why these settings matter:

- `Web Access` allows the participant to sign in directly to Database Actions in the browser
- `DWROLE` provides the common workshop privileges including create table, create view, create session, and `DBMS_CLOUD` execution support
- `Quota on DATA` allows the user to create and load tables during workshop exercises

Reference documentation:

- [Provision an Autonomous AI Database Instance](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/autonomous-provision.html)
- [Connect with Built-In Oracle Database Actions](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/connect-database-actions.html)
- [Create and Manage Users on Autonomous AI Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/manage-users-create.html)
- [Manage User Roles and Privileges on Autonomous AI Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/manage-users-privileges.html)

### Instructor-led Claims star schema build

Build and explain this star first:

- Fact: `mpha_fact_claims_monthly`
- Dimensions:
  - `mpha_dim_date`
  - `mpha_dim_district`
  - `mpha_dim_coverage_program`
  - `mpha_dim_claim_type`

Recommended joins:

- `mpha_fact_claims_monthly.service_month_date_key -> mpha_dim_date.date_key`
- `mpha_fact_claims_monthly.district_key -> mpha_dim_district.district_key`
- `mpha_fact_claims_monthly.program_key -> mpha_dim_coverage_program.program_key`
- `mpha_fact_claims_monthly.claim_type_key -> mpha_dim_claim_type.claim_type_key`

The role-tagged Lab 3 exercise steps above are the execution sequence to follow for the Claims star schema publish and validation flow.

### Lab 4 handoff

After the Claims star schema validation succeeds, move to the OAC lab.

Use these assets as the instructor-led OAC reference build:

- `dashboard_spec.md`
- `lab4_oac_executive_overview_build_guide.html`
- `assets/oac_dashboard_lab/screenshots/42_oac_live_consumer_assistant_denied_claims_additional_insights.png`

Important boundary:

- OAC Assistant answers questions about the indexed claims dataset.
- Questions that depend on the playbook document belong in the separate `Claims and Policy Copilot` optional lab.

## Lab 4 - Analyze Claims star schema in Oracle Analytics Cloud

### Objectives

- Connect OAC to the validated Claims star schema in Autonomous AI Lakehouse.
- Build the MPHA Claims Executive Overview canvas in OAC.
- Use KPI tiles with sparklines, business-question titles, and compact command-center spacing.
- Test OAC Assistant with claims-dataset questions only.

### Admin Preparation

Participants: you can skip this section if the facilitator has already prepared the OAC connection and dataset.

1. Create the shared OAC connection if one does not already exist.
   - In OAC, go to `Create -> Connection -> Oracle Autonomous AI Lakehouse`.
   - Use `TLS` for wallet-free connectivity or `Mutual TLS` if your environment requires a wallet upload.
   - Screenshot reference in the Lab 4 build guide: OAC home, Create menu, connection type, and AI Lakehouse connection form.
2. Create the instructor-led Claims star schema dataset.
   - In OAC, go to `Create -> Dataset`.
   - Select the Autonomous AI Lakehouse connection.
   - Expand the connected schema and select `mpha_fact_claims_monthly`, `mpha_dim_date`, `mpha_dim_district`, `mpha_dim_coverage_program`, and `mpha_dim_claim_type`.
   - Drag or double-click the five tables into the Join Diagram canvas.
   - Prepare the self-service data model by confirming that `mpha_fact_claims_monthly` is centered and connected to the four dimensions.
   - Right-click the fact table and select `Preserve Grain`.
   - Use the data profiling panel to confirm value distributions, nulls, and sample rows.
   - Save the dataset as `MPHAClaimAnalysis`.
   - Screenshot reference in the Lab 4 build guide: dataset connection selection, expanded Claims schema checkpoint, MPHA self-service Join Diagram, data profiling view, and workbook data panel verification.
3. Enable OAC Assistant at the dataset level if it is not already enabled.
   - Open the dataset in a workbook.
   - Right-click the dataset name in the data panel.
   - Open `Inspect -> Search`.
   - Set `Index Dataset For` to `Assistants and Homepage Search`.
   - Review the indexed field scope.
   - Click `Save` if changes were made, then `Run Now`.
   - Screenshot reference in the Lab 4 build guide: dataset context menu, Search settings, Search scope, and Assistant panel.

### Participant Steps

Use `lab4_oac_executive_overview_build_guide.html` as the screenshot-led participant guide. It follows the live OAC flow from Lakehouse connection through dataset modeling, data profiling, Assistant indexing, and the final Executive Overview dashboard canvas.

1. Open the provided `MPHAClaimAnalysis` dataset and create a workbook.
2. Rename the first canvas to `Executive Overview`.
3. Set the canvas layout to `Freeform`.
4. Add a title text box: `MPHA Claims Processing Command Center`.
5. Add dashboard filters for:
   - `DISTRICT_NAME`
   - `CLAIM_TYPE`
6. Create six KPI tile visuals with monthly sparklines:
   - `Claims submitted`
   - `Claims denied`
   - `Denial rate`
   - `Submitted amount`
   - `Paid amount`
   - `Processing days`
7. Add the denial hotspot heatmap:
   - title: `Where are denial-rate hotspots by program and claim type?`
   - rows: coverage program
   - columns: claim type
   - color: denial rate
8. Add the denied-claims district donut:
   - title: `Which districts contribute the most denied claims?`
   - value: denied claims
   - category: district name
9. Add the claim-type review table:
   - title: `Which claim types need denial review?`
   - columns: claim type, denied claims, denial rate
10. Add the bubble analysis:
   - title: `Do high-volume claim types also take longer or get denied more?`
   - group: claim type
   - x axis: claims submitted
   - y axis: average processing days
11. Add the denial-rate trend:
   - title: `How is the denial rate trending month over month?`
   - category: service month
   - measure: denial rate
12. Use round borders, light center shadows, equal spacing, and business-question titles across the canvas.
13. Save the workbook as `MPHA Claims Command Center`.

Reference build:

- `lab4_oac_executive_overview_build_guide.html`
- `dashboard_spec.md`
- `assets/oac_dashboard_lab/screenshots/42_oac_live_consumer_assistant_denied_claims_additional_insights.png`

### OAC Assistant Prompts

Use prompts like these after dataset indexing completes:

- "Which districts contribute the most denied claims, and what should the claims operations team prioritize?"
- "Which claim types need denial review?"
- "Compare denied claims and processing days by claim type."
- "How is denial rate trending by month?"

For the first Assistant prompt, expand `Additional Insights` before capturing the workshop checkpoint screenshot.

## Lab 4B - Extend Claims Analytics with JSON and Spatial Context

### Business Trigger

Round 1 answers the original Claims visibility requirement. After seeing the Claims dashboard, MPHA leadership asks whether denial hotspots are connected to facility capacity pressure and spatial access gaps.

The extension pattern is intentional: do not rebuild the Claims star schema. Add new raw formats, process them through AIDP, publish a district-level context table in AI Lakehouse, and extend OAC with additional insights.

### Inputs

- JSON raw data: `data/raw_json/facility_capacity_events.jsonl`
- Spatial raw data: `data/raw_spatial/healthcare_service_areas.geojson`
- Existing Bronze outputs from Lab 2
- Existing Claims star schema from Lab 3

### Bronze-to-Silver Extension

Run `notebooks/02B_Silver_Claims_Context_Extension.ipynb`.

Validated AIDP execution:

1. Create or upload `02B_Silver_Claims_Context_Extension.ipynb` in the `O2_Silver` folder.
2. Attach the active Spark cluster `E2EAIDPIndustrydemos`.
3. Run the notebook cell.
4. Confirm the output includes:
   - `Round 2 Silver context complete.`
   - `Wrote silver_operations_access_context to /Volumes/e2eindustrydemos/default/e2eindustrydemovol/Silver/silver_operations_access_context`

Screenshots captured:

- `assets/aidp_context_extension_lab/screenshots/04_silver_extension_notebook_attached.png`
- `assets/aidp_context_extension_lab/screenshots/05_silver_extension_success.png`

This notebook combines:

- `bronze_facility_capacity_events`
- `bronze_healthcare_service_areas_geojson`
- facility/provider reference data
- district reference data

It creates:

- `silver_operations_access_context`

Key enhancements:

- parse JSON event timestamp, hour, and day of week
- flatten triage category counts
- derive `triage_total`, `triage_acuity_score`, `supply_alert_count`, `diversion_event_flag`, and `capacity_pressure_band`
- explode GeoJSON features
- classify district boundary, facility point, and facility catchment features
- derive `facility_count`, `catchment_count`, `residents_per_facility`, `spatial_access_band`, and `access_gap_score`
- create a combined `operations_access_risk_score`

### Silver-to-Gold and AI Lakehouse Extension

Run `sql/create_ai_lakehouse_claims_context_extension.sql` first to create:

- `mpha_fact_district_claims_context`
- `mpha_claims_district_context_v`

Then run `notebooks/03B_Gold_Claims_Context_AI_Lakehouse_Extension.ipynb`.

Validated AIDP execution:

1. Create or upload `03B_Gold_Claims_Context_AI_Lakehouse_Extension.ipynb` in the `03a_GoldAILHLoad` folder.
2. Attach the active Spark cluster `E2EAIDPIndustrydemos`.
3. Confirm the AI Lakehouse extension table exists before the insert.
4. Run the notebook cell.
5. Confirm the output includes:
   - `Wrote Gold context Delta output to /Volumes/e2eindustrydemos/default/e2eindustrydemovol/gold_stage/gold_district_claims_context`
   - `Wrote 5 new rows to goldailh.e2eaidpuser.mpha_fact_district_claims_context`
   - `Round 2 Gold context complete.`

Screenshots captured:

- `assets/aidp_context_extension_lab/screenshots/06_gold_extension_notebook_attached.png`
- `assets/aidp_context_extension_lab/screenshots/07_gold_extension_success.png`

It creates:

- `gold_district_claims_context`
- AI Lakehouse rows in `mpha_fact_district_claims_context`

The grain is district-month, aligned to the existing Claims star schema dimensions.

Key enhancements:

- aggregate capacity pressure by district-month
- aggregate Claims denial and processing metrics by district-month
- calculate `claims_context_priority_score`
- recommend district action such as claims review, provider outreach, or mobile clinic scheduling

### Validation

Run `sql/claims_context_extension_validation.sql`.

Expected checks:

- context rows are loaded
- district and month counts are non-zero
- priority districts show combined Claims, capacity, and spatial access signals

Validated output:

- `mpha_fact_district_claims_context` returned 5 AI Lakehouse rows.
- `mpha_claims_district_context_v` returned 5 OAC-ready rows.

Screenshots captured:

- `assets/aidp_context_extension_lab/screenshots/08_gold_extension_validation.png`
- `assets/aidp_context_extension_lab/screenshots/09_context_view_validation.png`

### OAC Extension

Add `mpha_claims_district_context_v` to the existing Claims analytics workbook as a supporting dataset or a new context canvas.

Use business-question visuals such as:

- "Which denial hotspots also have high capacity pressure?"
- "Which districts combine high denial rate and poor spatial access?"
- "Where should MPHA prioritize claims review, provider outreach, and mobile clinic intervention together?"

The original Executive Overview canvas remains unchanged. The Round 2 context is added as an extension.

### DIY Facility Access Daily Dashboard Challenge

After the guided OAC walkthrough, participants create their own dashboard for Facility Access Daily. The facilitator should not provide the complete dashboard build because this is the participant understanding check.

### DIY Build Target

- Fact: `mpha_fact_facility_access_daily`
- Dimensions:
  - `mpha_dim_date`
  - `mpha_dim_facility`
  - `mpha_dim_district`
  - `mpha_dim_pressure_band`

### Participant Challenge Prompts

- Build a facility dashboard that answers which facilities are missing wait-time targets.
- Show occupancy, staffing pressure, and access risk by facility and district.
- Decide which filters are needed for a useful operator workflow.
- Explain why the fact keeps `district_key` directly in the fact row.

### Discussion Prompts

Use prompts like these during the participant challenge discussion. Claims-only questions can be asked in OAC Assistant after dataset indexing; document or playbook-dependent questions should be saved for the Claims and Policy Copilot lab.

- "Summarize the top three districts with the highest public-health pressure this month."
- "Explain which facilities are most likely to need staffing support based on occupancy and overtime."
- "Identify immunization equity gaps for older residents and recommend outreach actions."
- "Describe the relationship between respiratory positivity and emergency department wait times."
- "Which districts should receive mobile clinic sessions based on spatial access and current pressure?"
- "Use the MPHA playbook to explain what action is recommended when occupancy and ED waits rise together."
- "Which coverage programs have the highest claim denial rates and what operational follow-up is needed?"
- "Which claim types take the longest to adjudicate?"
- "Which districts show the largest claims leakage between submitted and paid amounts?"

### Expected Outcome

You have an instructor-led Claims star schema workbook and a participant-built Facility Access Daily dashboard challenge grounded in the same Bronze and Silver design pattern.

## Optional Lab 5 - Claims Denial Risk Scoring

Use `optional_labs/claims_denial_risk_scoring.md` and `data/gold/gold_claims_denial_risk_scores.csv`.

### Objectives

- Derive ML-ready features from claims, event, district, and provider-accreditation context.
- Produce a score that estimates which district-program-claim-type combinations are most likely to need manual review.
- Publish compact scoring outputs that can be added to the Claims star schema story in OAC.

### Admin Preparation

Participants: you can skip this section if the facilitator has already prepared the ML folder, cluster, and source objects.

1. Confirm that the claims-serving Gold outputs, spatial insight outputs, and provider-accreditation outputs are available.
2. Confirm that the shared Spark cluster and the `04_ML` folder are ready for participant use.

### Participant Steps

1. Create or upload a Spark notebook in the `04_ML` folder and attach the workshop Spark cluster.
2. Use `notebooks/aidp_ml_claims_denial_risk_pyspark.py` as the starter ML notebook.
3. Load `gold_claims_summary`, `gold_capacity_event_latest`, `gold_provider_accreditation_summary`, and `gold_spatial_access_insights`.
4. Build the training frame at Claims star schema grain:
   - service month
   - district
   - coverage program
   - claim type
5. Derive scoring features such as denial rate, average processing days, payment yield, triage total, supply alert count, public health pressure index, and accreditation risk band.
6. Define the first target such as `high_denial_flag` or `denial_risk_score`.
7. Train a simple baseline model using historical months.
8. Score the newest month and create:
   - `denial_risk_score`
   - `likely_denial_bucket`
   - `review_priority`
9. Publish the result as `gold_claims_denial_risk_scores.csv` or an equivalent serving table.
10. Register the selected run as `claim_denial_risk` in AIDP Models, version `v1`.
11. Blend the output back into the instructor-led Claims star schema story in OAC.

### Expected Outcome

You can explain how AI Data Platform notebooks can score denial risk from the curated Gold layer and show how review teams can prioritize follow-up using `denial_risk_score`, `likely_denial_bucket`, and `review_priority`.

## Optional Lab 6A - Prepare the Claims Policy RAG Knowledge Base

Use `optional_labs/claims_policy_copilot_agent.md`, `documents/MPHA_Winter_Respiratory_Response_Playbook.docx`, and the Claims star schema Gold objects.

### Objectives

- Prepare an AIDP knowledge base from the MPHA playbook document.
- Expose the playbook document from Object Storage through the AIDP external volume.
- Chunk and ingest the document into a searchable knowledge base for RAG grounding.

### Admin Preparation

Participants: you can skip this section if the facilitator has already prepared the Object Storage/external-volume source and the knowledge base.

1. Confirm the playbook document is available in Object Storage and exposed through the AIDP external volume.
2. Confirm `e2eindustrydemos.default.mphapolicy` exists or can be created in the AIDP standard catalog schema.

### Participant Steps

1. Open AIDP Workbench, go to **Master catalog**, and open `e2eindustrydemos.default`.
2. Open **Volumes**, then `e2eindustrydemovol`, and confirm `RawData` contains `MPHA_Winter_Respiratory_Response_Playbook.docx`.
3. Return to `e2eindustrydemos.default`, choose **Add to schema > Knowledge base**, and create `mphapolicy`.
4. In `mphapolicy`, add the `RawData` folder as a data source.
5. Keep the supported document filters enabled, including `DOCX`, and start ingestion.
6. Confirm the latest ingestion job run shows `Succeeded`.
7. Record the knowledge base path: `e2eindustrydemos.default.mphapolicy`.

### Expected Outcome

The MPHA playbook is available as a searchable AIDP knowledge base and can be selected by the RAG tool in Optional Lab 6B.

## Optional Lab 6B - Claims and Policy Copilot

Use `optional_labs/claims_policy_copilot_agent.md`, the Claims star schema Gold objects, and the knowledge base from Optional Lab 6A.

### Objectives

- Build a copilot that can answer claims, policy, and operational follow-up questions in natural language.
- Query curated Claims star schema data with a SQL tool.
- Ground policy and operating answers with the vectorized playbook through a RAG tool.
- Validate SQL-only, RAG-only, and combined supervisor-agent questions.

### Admin Preparation

Participants: you can skip this section if the facilitator has already prepared the claims-serving scope, the knowledge base, and the agent AI compute.

1. Confirm the claims-serving Gold objects are queryable in Autonomous AI Lakehouse.
2. Confirm `e2eindustrydemos.default.mphapolicy` exists from Optional Lab 6A.
3. Confirm the facilitator can access AIDP Agent flows and the AI compute used for testing.

### Participant Steps

1. Create or open the `MPHA_Claims_Policy_Copilot` agent shell.
2. Add a SQL tool that is limited to the approved Claims star schema tables.
3. Add a RAG tool connected to `e2eindustrydemos.default.mphapolicy`.
4. Add a supervisor agent, a SQL executor, and a RAG executor.
5. Deploy the agent flow to active AI compute.
6. Test three question types: SQL-only, policy-only, and combined claims-and-policy.
7. Use the copilot as a sidecar experience during the workshop and explain how it differs from OAC Assistant.

### Expected Outcome

You can explain a practical agent pattern for this workshop: AI Data Platform prepares the Gold layer, stores playbook chunks in an AIDP knowledge base, and runs an executable SQL-plus-RAG copilot grounded in the curated Claims star schema and the MPHA playbook.

## Facilitator Extension - Governance and Operationalization

### Admin Steps

Participants: this is primarily a facilitator or platform-owner extension lab.

1. Add data quality checks for missing dates, invalid rates, and impossible occupancy values.
2. Schedule the Bronze, Silver, and Gold Spark jobs through the AIDP workflow described in `workflows/aidp_incremental_medallion_workflow.md`.
3. Create OAC alerts for high occupancy or high pressure index.
4. Document the synthetic-data privacy boundary for demo and training usage.

## Success Criteria

You have completed the workshop when you can:

- Explain the MPHA business use case.
- Trace data from raw files to Bronze, Silver, and Gold layers.
- Explain how Claims star schema and Facility Access Daily star schema branch from the same Silver foundation.
- Analyze claims signals from the Gold schema.
- Build the instructor-led Claims star schema workbook in OAC.
- Create your own Facility Access Daily dashboard as a participant challenge.
- Explain the optional ML scoring and Claims and Policy Copilot extension patterns.
