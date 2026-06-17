# Accelerate Public Healthcare Analytics with Generative AI, AI Data Platform, and Autonomous AI Lakehouse

## About This Workshop

Public healthcare organizations need to balance service access, clinical capacity, staffing, immunization campaigns, claims adjudication, public-program disbursement, membership eligibility, provider accreditation, and emerging public-health risks. In this workshop, you will build a lakehouse analytics pipeline for Metro Public Health Authority (MPHA), a fictional public healthcare network serving five districts through hospitals, urgent-care centers, and community clinics.

You will load synthetic healthcare operations data, refine it through a medallion architecture using Spark and Delta Lake in Oracle AI Data Platform, serve the Gold business layer through a dimensional snowflake schema in Autonomous AI Lakehouse, and build dashboards in Oracle Analytics Cloud (OAC). The final dashboard helps leaders identify where service pressure is rising, where access is uneven, and which facilities or districts need operational intervention.

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
- Optional: OCI GoldenGate
- Optional: OCI Streaming or Kafka-compatible streaming source

**Dataset period:** January 1, 2025 to June 30, 2025

**Dataset type:** Five synthetic CSV datasets, one JSONL event dataset, one GeoJSON spatial dataset, and one synthetic operating playbook document

## Architecture

1. Raw CSV, JSONL, GeoJSON, document, and optional streaming sample files are uploaded to object storage as the immutable landing zone.
2. AI Data Platform creates the **Bronze** layer as schema-preserving Delta tables with ingestion metadata.
3. AI Data Platform creates the **Silver** layer as conformed Delta tables with typed fields, quality rules, reference joins, spatial feature extraction, document chunk metadata, and derived operational flags.
4. Autonomous AI Lakehouse hosts the **Gold** layer as a snowflake / fact constellation schema with shared dimensions, business facts, spatial planning insights, document-chat context, real-time event summaries, and OAC-ready views.
5. OAC connects to the Gold layer and presents dashboard tabs, filters, spatial insights, and grounded chat with data and documents for public-health leaders.

## Lab 1 - Create a Healthcare Lakehouse with AI Data Platform

### Objectives

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

### Tasks

1. Create object storage folders such as `mpha/raw/`, `mpha/raw_json/`, `mpha/raw_spatial/`, and `mpha/documents/`.
2. Upload the five CSV files, one JSONL file, one GeoJSON file, and one DOCX file.
3. Open AI Data Platform and create a Spark notebook.
4. Use `notebooks/aidp_bronze_pyspark.py` as the starter notebook.
5. Set the `raw_base`, `raw_json_base`, `raw_spatial_base`, `document_base`, and `bronze_base` paths to your object storage locations.
6. Read each source and confirm row counts match `manifest.json`.

### Expected Outcome

You have a raw healthcare data lake layer that contains exactly five CSV datasets, one JSONL capacity-event dataset, one GeoJSON spatial dataset, and one document.

## Lab 2 - Build Bronze and Silver Layers with AI Data Platform

### Objectives

- Convert raw CSV files into Bronze Delta tables without changing source values.
- Add ingestion metadata such as source file, batch id, and load timestamp.
- Create Silver Delta tables with clean, typed, conformed healthcare data.
- Add derived measures for access risk, wait-time variance, high occupancy, immunization completion, and public-health pressure.
- Extract spatial features from GeoJSON and prepare a spatial access insight.
- Prepare playbook document chunks for vector search and grounded chat.

### Notebook sequence

1. Run `notebooks/aidp_bronze_pyspark.py` to write raw-preserving Bronze Delta tables.
2. Run `notebooks/aidp_silver_pyspark.py` to type, validate, and conform the healthcare data into Silver Delta tables.
3. Keep `notebooks/aidp_refinement_pyspark.py` only as a legacy combined reference if a facilitator wants one file instead of the split flow.

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

### Gold Layer in Autonomous AI Lakehouse

Gold is the business serving layer. The recommended model is a dimensional snowflake schema in Autonomous AI Lakehouse so OAC connects to shared, reusable dimensions and facts rather than notebook outputs or isolated flat files.

The package also includes flat Gold mart samples in `data/gold/` for quick validation, but the workshop execution path should use `data/gold_dimensional/` and `sql/create_ai_lakehouse_dimensional_gold_schema.sql`.

### Gold Dimensions

| Dimension | Grain | Purpose |
| --- | --- | --- |
| `mpha_dim_date` | Date | Shared service date, week start, month, quarter, and year attributes. |
| `mpha_dim_district` | District | District population, deprivation, elderly share, chronic-condition share, and income context. |
| `mpha_dim_facility` | Facility | Facility master data, coordinates, licensed beds, wait targets, and `district_key`. |
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
| `mpha_fact_facility_access_daily` | Facility-day | Date, Facility, Pressure Band | Daily access, wait, capacity, staffing, satisfaction, and access risk. |
| `mpha_fact_district_public_health_weekly` | District-week | Date, District, Pressure Band | Public-health pressure, immunization completion, no-show, positivity, and respiratory ED demand. |
| `mpha_fact_immunization_equity_weekly` | District-week-age group | Date, District, Age Group | Campaign reach and equity analysis by district and age group. |
| `mpha_fact_quality_event_summary` | Facility-event type-severity | Facility, Quality Event | Service-quality volume, closure time, SLA breach, and readmission indicators. |
| `mpha_fact_spatial_access_insight` | District | District, Pressure Band | Residents per facility, distance, pressure, and mobile-clinic planning recommendations. |
| `mpha_fact_capacity_event` | Facility-event | Date, Facility, Pressure Band | JSON capacity-event signals for real-time operations views. |
| `mpha_fact_stream_wait_time_minute` | Facility-minute | Date, Facility, Pressure Band | Optional Kafka/AIDP streaming wait-time metrics. |
| `mpha_bridge_chat_topic_chunk` | Question-chunk | Document Chunk | Bridge table linking chat prompts to retrieved playbook chunks. |
| `mpha_fact_claims_monthly` | District-month-program-claim type | Date, District, Coverage Program, Claim Type | Claims volume, approval, denial, pending, payment yield, and processing time. |
| `mpha_fact_disbursement_monthly` | District-month-program-payee type | Date, District, Coverage Program | Public-program disbursement count, amount, pending, failed, and payment-cycle metrics. |
| `mpha_fact_membership_snapshot` | District-program-member segment snapshot | Date, District, Coverage Program, Member Segment | Membership, active eligibility, renewals due, suspended members, and high-risk members. |
| `mpha_fact_provider_accreditation` | Facility-provider accreditation snapshot | Date, Facility, Accreditation Status, Pressure Band | Accreditation score, corrective actions, days to expiry, and accreditation risk band. |

This is a snowflake because facility attributes roll up to district through `mpha_dim_facility.district_key`, while district-grain facts join directly to `mpha_dim_district`.

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
- Load the dimensional Gold schema in Autonomous AI Lakehouse using `sql/create_ai_lakehouse_dimensional_gold_schema.sql`.
- Use `sql/create_ai_lakehouse_gold_layer.sql` only if a facilitator wants the simpler flat-mart path for comparison.

### Expected Outcome

You have Bronze and Silver Delta layers in AI Data Platform and a dimensional Gold serving layer in Autonomous AI Lakehouse, including spatial planning, real-time event, and document-chat serving objects.

## Lab 3 - Gather Insights from Gold Layer with Oracle Analytics Cloud

### Objectives

- Connect OAC to Autonomous AI Data Lakehouse.
- Build a semantic model from the dimensional Gold tables and OAC-ready star views.
- Create dashboard canvases for operational leaders and public-health teams.
- Use natural-language or generative summaries to explain high-risk areas.
- Add a spatial planning view using `gold_spatial_access_insights`.
- Add a chat-with-data-and-documents view using `gold_document_chat_context` and the playbook chunks.

### Gold staging sequence

1. Run `notebooks/aidp_gold_pyspark.py` after the Silver notebook completes.
2. Set the `silver_base` and `gold_stage_base` paths to your object storage locations.
3. Stage Gold-serving outputs for facility access, district public health, claims, disbursement, membership, provider accreditation, spatial planning, and latest capacity events.
4. Load the dimensional Gold schema with `sql/create_ai_lakehouse_dimensional_gold_schema.sql`.

### Recommended OAC Canvases

1. **Executive Overview**
   - Total visits
   - Average ED wait time
   - Facilities over occupancy threshold
   - Public-health pressure by district

2. **Access and Capacity**
   - Wait-time variance by facility
   - Bed occupancy trend
   - Overtime hours vs occupancy
   - Access risk score by district

3. **Immunization Equity**
   - Doses administered by district and age group
   - Completion rate trend
   - Immunization no-show rate by district
   - Eligible population vs administered doses

4. **Surveillance and Service Quality**
   - Positivity rate trend
   - Respiratory-related ED visits
   - Quality events by severity and type
   - Average days to close quality events

5. **Spatial Insights**
   - Residents per facility by district
   - District pressure map
   - Catchment planning recommendation
   - Mobile clinic candidate list

6. **Chat with Data and Documents**
   - Suggested questions
   - Retrieved playbook sections
   - Structured Gold metrics used as context
   - Grounded response and recommended action

7. **Real-Time Operations**
   - Latest capacity JSON events
   - Streaming wait-time pressure band
   - Queue depth and occupancy
   - Optional GoldenGate or Kafka/AIDP status indicators

8. **Claims, Disbursement, Membership and Provider Accreditation**
   - Claims submitted, denied, approved, pending, and paid by coverage program
   - Disbursement amount, pending payments, failed payments, and payment cycle time
   - Active members, renewal-due members, high-risk members, and suspended eligibility
   - Provider accreditation score, corrective actions, days to expiry, and risk band

### Generative Analytics Prompts

Use prompts like these in OAC narrative or assistant features:

- "Summarize the top three districts with the highest public-health pressure this month."
- "Explain which facilities are most likely to need staffing support based on occupancy and overtime."
- "Identify immunization equity gaps for older residents and recommend outreach actions."
- "Describe the relationship between respiratory positivity and emergency department wait times."
- "Which districts should receive mobile clinic sessions based on spatial access and current pressure?"
- "Use the MPHA playbook to explain what action is recommended when occupancy and ED waits rise together."
- "Which coverage programs have the highest claim denial rates and what operational follow-up is needed?"
- "Which districts have the most membership renewals due in the next 60 days?"
- "Which accredited providers should be prioritized for corrective-action review?"

### Expected Outcome

You have a public-health analytics dashboard that helps leaders prioritize capacity, staffing, outreach, and service-quality interventions.

## Optional Lab 4 - Real-Time Analytics with OCI GoldenGate

Use `optional_labs/real_time_analytics_golden_gate.md` and `sql/realtime_gold_tables.sql`.

### Objectives

- Capture synthetic appointment, encounter, bed-status, and quality-event changes from an operational source.
- Deliver changes with OCI GoldenGate to a target stream, object-storage path, or AI Lakehouse staging table.
- Publish compact real-time Gold objects for OAC.

### Expected Outcome

You can explain where GoldenGate fits for transactional change-data capture and show how real-time operational changes can feed the OAC Real-Time Operations tab.

## Optional Lab 5 - Stream Analytics with Kafka-Compatible Streaming via AIDP

Use `optional_labs/stream_analytics_kafka_aidp.md`, `data/streaming/wait_time_events.jsonl`, `notebooks/aidp_kafka_streaming_pyspark.py`, and `sql/realtime_gold_tables.sql`.

### Objectives

- Publish wait-time events to a Kafka-compatible stream.
- Use AIDP Structured Streaming to build Bronze, Silver, and Gold stream layers.
- Feed the OAC Real-Time Operations tab with minute-level pressure metrics.

### Expected Outcome

You can explain the streaming medallion pattern and show how telemetry-style events differ from GoldenGate change-data capture.

## Optional Lab 6 - Governance and Operationalization

- Add data quality checks for missing dates, invalid rates, and impossible occupancy values.
- Schedule the Bronze, Silver, and Gold Spark jobs.
- Create OAC alerts for high occupancy or high pressure index.
- Document the synthetic-data privacy boundary for demo and training usage.

## Success Criteria

You have completed the workshop when you can:

- Explain the MPHA business use case.
- Trace data from raw files to Bronze, Silver, and Gold layers.
- Query operational and public-health metrics in SQL.
- Use spatial data to identify a mobile-clinic or outreach planning insight.
- Use vectorized document chunks to support a chat-with-data-and-documents use case.
- Analyze claims, disbursement, membership, and provider accreditation signals from the Gold schema.
- Build OAC dashboards with working tabs and filters that answer leadership questions.
- Explain the optional GoldenGate and Kafka/AIDP real-time analytics patterns.
