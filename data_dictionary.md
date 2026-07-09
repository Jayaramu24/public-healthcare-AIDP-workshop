# Data Dictionary

## Raw Files

The simplified source package intentionally keeps the landing zone small: five CSV datasets, one JSONL dataset, one GeoJSON dataset, and one DOCX document.

### `data/raw/district_health_profile.csv`

Grain: one row per district.

| Column | Description |
| --- | --- |
| `district_id` | Stable district identifier. |
| `district_name` | District display name. |
| `population` | Synthetic resident population. |
| `deprivation_index` | Relative need index from 0 to 1. Higher values indicate higher socioeconomic need. |
| `elderly_pct` | Share of residents age 65 and older. |
| `chronic_condition_pct` | Estimated share of residents with chronic conditions. |
| `median_income_usd` | Synthetic median income. |

### `data/raw/facility_provider_master.csv`

Grain: one row per facility/provider.

Business flavor: facility master data plus Healthcare Provider Accreditation.

| Column | Description |
| --- | --- |
| `facility_id`, `facility_name`, `facility_type`, `district_id` | Facility identifier, display name, type, and district. |
| `latitude`, `longitude` | Approximate synthetic coordinates. |
| `licensed_beds`, `baseline_daily_visits` | Capacity and baseline demand context. |
| `target_ed_wait_minutes`, `target_outpatient_wait_minutes` | Service access targets. |
| `provider_id`, `provider_name` | Synthetic provider identifier and name. |
| `accreditation_body`, `accreditation_status`, `accreditation_level` | Accreditation context. |
| `last_survey_date`, `expiry_date` | Survey and accreditation expiry dates. |
| `accreditation_score`, `corrective_action_count`, `specialty_scope` | Provider oversight and corrective-action measures. |

### `data/raw/facility_operations_daily.csv`

Grain: one row per facility per day.

| Column | Description |
| --- | --- |
| `service_date` | Day of service. |
| `facility_id` | Facility identifier. |
| `outpatient_visits` | Daily outpatient volume. |
| `emergency_arrivals` | Daily ED or urgent emergency arrivals. |
| `admissions`, `discharges` | Daily inpatient flow. |
| `avg_ed_wait_minutes` | Average ED wait time in minutes. |
| `avg_outpatient_wait_minutes` | Average outpatient wait time in minutes. |
| `no_show_rate` | Share of scheduled visits missed. |
| `bed_occupancy_rate` | Occupied beds divided by licensed beds. |
| `staff_hours` | Total daily staff hours. |
| `overtime_hours` | Daily overtime hours. |
| `patient_satisfaction_score` | Synthetic service satisfaction score from 0 to 100. |
| `quality_event_count` | Count of service-quality events on the same facility-day. |
| `high_severity_quality_events` | Count of high-severity service-quality events. |
| `avg_days_to_close_quality_events` | Average closure days for events on the same facility-day. |
| `avoidable_readmission_events` | Count of avoidable-readmission-related quality events. |

### `data/raw/population_health_weekly.csv`

Grain: one row per district, week, and age group.

Business flavor: immunization equity and respiratory surveillance in one weekly source.

| Column | Description |
| --- | --- |
| `week_start_date` | Start date of reporting week. |
| `district_id` | District identifier. |
| `age_group` | Population age band. |
| `eligible_population` | Eligible population estimate for the campaign. |
| `appointments_booked` | Booked immunization appointments. |
| `missed_appointments` | Booked appointments not attended. |
| `walk_in_visits` | Unscheduled walk-in immunization visits. |
| `doses_administered` | Total administered doses. |
| `tests_reported` | Respiratory tests reported. |
| `positive_tests` | Positive respiratory tests. |
| `positivity_rate` | Positive tests divided by reported tests. |
| `respiratory_related_ed_visits` | ED visits associated with respiratory illness. |

### `data/raw/claims_membership_disbursement.csv`

Grain: one synthetic claim transaction.

Business flavor: claims adjudication, disbursement, membership eligibility, coverage program, and member risk segmentation in one source.

| Column | Description |
| --- | --- |
| `claim_id` | Synthetic claim identifier. |
| `member_id` | Synthetic member identifier; no names, addresses, birth dates, or PHI are included. |
| `facility_id`, `provider_id`, `district_id` | Provider and geography references. |
| `service_date`, `claim_received_date` | Service and received dates. |
| `program_code`, `coverage_program`, `program_type`, `funding_source` | Public healthcare coverage program context. |
| `claim_type`, `service_category`, `diagnosis_group` | Coarse claim/service classification. |
| `submitted_amount`, `approved_amount`, `paid_amount` | Synthetic claim financial amounts. |
| `claim_status`, `denial_reason`, `processing_days` | Adjudication result and cycle-time fields. |
| `primary_facility_id`, `enrollment_date`, `renewal_due_date` | Membership and preferred-facility context. |
| `eligibility_status` | Active, Renewal Due, or Suspended. |
| `age_group`, `risk_segment`, `chronic_condition_flag` | Member segmentation for analysis. |
| `disbursement_id`, `payee_type`, `disbursement_date` | Claim-linked payment execution context. |
| `disbursement_amount`, `payment_method`, `payment_status`, `payment_cycle_days` | Disbursement amount, status, method, and cycle time. |

## Raw JSON Files

### `data/raw_json/facility_capacity_events.jsonl`

Grain: one row per facility capacity event.

| Field | Description |
| --- | --- |
| `event_id` | Capacity event identifier. |
| `event_timestamp` | Source event timestamp in UTC. |
| `facility_id` | Facility identifier. |
| `source_system` | Synthetic source system for the event. |
| `current_occupancy_rate` | Current occupancy signal from the command center. |
| `waiting_room_count` | Current waiting-room count. |
| `avg_ed_wait_minutes` | Current average ED wait-time signal. |
| `triage_category_counts` | Nested object with resuscitation, emergent, urgent, and standard counts. |
| `supply_alerts` | Array of active supply alerts. |
| `ambulance_diversion_status` | Boolean signal for diversion status. |

## Raw Spatial Files

### `data/raw_spatial/healthcare_service_areas.geojson`

Grain: one GeoJSON FeatureCollection containing district boundary, facility point, and facility catchment features.

Key properties include `source_layer`, `district_id`, `district_name`, `facility_id`, `facility_name`, `facility_type`, `catchment_population_estimate`, `access_risk_score`, and current pressure indicators depending on feature type.

## Document Source

### `documents/MPHA_Winter_Respiratory_Response_Playbook.docx`

Grain: a synthetic public-health operating playbook with a minimum of 13 pages. The document is used to demonstrate document ingestion, chunking, vectorization, retrieval, and grounded chat with data and documents.

## Silver-Style Generated Sample Files

### `data/curated/dim_facility.csv`

Facility dimension enriched with district population, deprivation, elderly share, and chronic-condition share.

### `data/curated/fact_facility_day.csv`

Facility-day fact table with operational metrics plus:

- `district_id`
- `facility_type`
- `ed_wait_variance_minutes`
- `outpatient_wait_variance_minutes`
- `high_occupancy_flag`
- `access_risk_score`

### `data/curated/fact_immunization_week.csv`

District-week-age group immunization fact table plus:

- `completion_rate`
- `immunization_no_show_rate`

### `data/curated/fact_district_health_week.csv`

District-week public-health fact table combining immunization and respiratory surveillance plus:

- `district_name`
- `district_population`
- `completion_rate`
- `immunization_no_show_rate`
- `public_health_pressure_index`

## Gold Files

The flat Gold files are sample AI Lakehouse-ready business marts generated from the Silver-style outputs. They are retained for quick validation and comparison.

The recommended workshop serving model is the dimensional Gold schema in `data/gold_dimensional/`, loaded with `sql/create_ai_lakehouse_dimensional_gold_schema.sql`.

## Gold Dimensional Files

### Dimensions

| File | Grain | Notes |
| --- | --- | --- |
| `data/gold_dimensional/dim_date.csv` | Date | Shared date dimension with calendar year, quarter, month, week start, day name, and week-start flag. |
| `data/gold_dimensional/dim_district.csv` | District | District attributes including population, deprivation, elderly share, chronic-condition share, and income. |
| `data/gold_dimensional/dim_facility.csv` | Facility | Facility attributes including type, district identifiers, coordinates, licensed beds, and wait targets. |
| `data/gold_dimensional/dim_age_group.csv` | Age group | Immunization age-band labels and sort order. |
| `data/gold_dimensional/dim_quality_event.csv` | Event type and severity | Conformed quality event category and severity. |
| `data/gold_dimensional/dim_pressure_band.csv` | Pressure band | Watch, Medium, and High operating pressure bands. |
| `data/gold_dimensional/dim_document_chunk.csv` | Document chunk | Playbook chunk text, page, section, embedding model, and embedding JSON. |
| `data/gold_dimensional/dim_coverage_program.csv` | Coverage program | Program code, public coverage program, program type, and funding source. |
| `data/gold_dimensional/dim_claim_type.csv` | Claim type | Claim type, service category, and coarse diagnosis group. |
| `data/gold_dimensional/dim_member_segment.csv` | Member segment | Age group, risk segment, and chronic-condition flag. |
| `data/gold_dimensional/dim_accreditation_status.csv` | Accreditation status | Accreditation body, status, level, and specialty scope. |

### Facts and Bridge Tables

| File | Grain | Main keys |
| --- | --- | --- |
| `data/gold_dimensional/fact_facility_access_daily.csv` | Facility-day | `date_key`, `facility_key`, `district_key`, `pressure_band_key` |
| `data/gold_dimensional/fact_district_public_health_weekly.csv` | District-week | `week_start_date_key`, `district_key`, `pressure_band_key` |
| `data/gold_dimensional/fact_immunization_equity_weekly.csv` | District-week-age group | `week_start_date_key`, `district_key`, `age_group_key` |
| `data/gold_dimensional/fact_quality_event_summary.csv` | Facility-quality event | `facility_key`, `district_key`, `quality_event_key` |
| `data/gold_dimensional/fact_spatial_access_insight.csv` | District | `district_key`, `pressure_band_key` |
| `data/gold_dimensional/fact_capacity_event.csv` | Facility-event | `event_date_key`, `facility_key`, `district_key`, `pressure_band_key` |
| `data/gold_dimensional/bridge_chat_topic_chunk.csv` | Chat question to document chunk | `document_chunk_key` |
| `data/gold_dimensional/fact_claims_monthly.csv` | District-month-program-claim type | `service_month_date_key`, `district_key`, `program_key`, `claim_type_key` |
| `data/gold_dimensional/fact_disbursement_monthly.csv` | District-month-program-payee type | `disbursement_month_date_key`, `district_key`, `program_key` |
| `data/gold_dimensional/fact_membership_snapshot.csv` | District-program-member segment snapshot | `snapshot_date_key`, `district_key`, `program_key`, `member_segment_key` |
| `data/gold_dimensional/fact_provider_accreditation.csv` | Facility-provider accreditation snapshot | `snapshot_date_key`, `facility_key`, `district_key`, `accreditation_status_key`, `pressure_band_key` |

### Dimensional Model Notes

- The schema is a star because facility-grain facts carry `district_key` directly and join straight to conformed dimensions without dimension-to-dimension joins.
- District-grain facts join directly to `dim_district`.
- Date, pressure band, and document chunk dimensions are shared across use cases.
- The model also behaves as a fact constellation because several business processes reuse common dimensions.
- Claims, disbursement, membership, and provider accreditation facts reuse district, facility, date, pressure-band, and program dimensions so OAC can filter payer and provider oversight measures with the same workbook controls.

## Flat Gold Compatibility Files

In the workshop, flat Gold files may be loaded with `sql/create_ai_lakehouse_gold_layer.sql` if a facilitator wants a simpler validation path.

### `data/gold/gold_facility_access_daily.csv`

Grain: one row per facility per day.

Business purpose: daily access, capacity, wait-time, staffing, satisfaction, and access-risk analysis.

Key columns:

- `service_date`
- `facility_id`, `facility_name`, `facility_type`
- `district_id`, `district_name`
- `outpatient_visits`, `emergency_arrivals`, `admissions`, `discharges`
- `avg_ed_wait_minutes`, `avg_outpatient_wait_minutes`
- `ed_wait_variance_minutes`, `outpatient_wait_variance_minutes`
- `bed_occupancy_rate`, `high_occupancy_flag`
- `staff_hours`, `overtime_hours`
- `patient_satisfaction_score`, `access_risk_score`

### `data/gold/gold_district_public_health_weekly.csv`

Grain: one row per district per week.

Business purpose: district-level public-health pressure, respiratory surveillance, and immunization campaign monitoring.

Key columns:

- `week_start_date`
- `district_id`, `district_name`, `district_population`
- `eligible_population`, `appointments_booked`, `missed_appointments`, `doses_administered`
- `completion_rate`, `immunization_no_show_rate`
- `tests_reported`, `positive_tests`, `positivity_rate`
- `respiratory_related_ed_visits`, `public_health_pressure_index`

### `data/gold/gold_immunization_equity_weekly.csv`

Grain: one row per district, week, and age group.

Business purpose: immunization equity analysis by age group and district.

### `data/gold/gold_quality_event_summary.csv`

Grain: one row per facility, severity, and event type.

Business purpose: service-quality event volumes, closure times, SLA breaches, and avoidable readmission indicators.

### `data/gold/gold_executive_overview.csv`

Grain: one row per district.

Business purpose: executive KPI tiles and district comparison summaries.

### `data/gold/gold_spatial_access_insights.csv`

Grain: one row per district.

Business purpose: spatial planning insight that combines district population, facility count, residents per facility, approximate distance, public-health pressure, and a mobile-clinic planning recommendation.

Key columns:

- `district_id`, `district_name`, `population`
- `facility_count`, `residents_per_facility`
- `avg_distance_to_facility_km`
- `public_health_pressure_index`
- `high_pressure_facilities`
- `spatial_business_insight`

### `data/gold/gold_capacity_event_latest.csv`

Grain: one row per facility capacity JSON event.

Business purpose: OAC Real-Time Operations preview using typed JSON event signals.

Key columns:

- `event_timestamp`
- `facility_id`, `facility_name`
- `district_id`, `district_name`
- `current_occupancy_rate`
- `waiting_room_count`
- `avg_ed_wait_minutes`
- `triage_total`
- `supply_alert_count`
- `ambulance_diversion_status`
- `capacity_pressure_band`

### `data/gold/gold_document_chat_context.csv`

Grain: one row per playbook document chunk.

Business purpose: AI Lakehouse serving context for chat with data and documents.

Key columns:

- `document_id`, `chunk_id`
- `page_number`, `section_title`
- `chunk_text`
- `embedding_model`
- `embedding_json`

### `data/gold/gold_claims_denial_risk_scores.csv`

Grain: one row per service month, district, coverage program, and claim type score slice.

Business purpose: optional machine learning scoring output that prioritizes likely denial hotspots for claims review teams.

Key columns:

- `service_month`
- `district_id`, `district_name`
- `program_code`, `coverage_program`
- `claim_type`
- `claims_submitted`, `denied_claims`, `denial_rate`
- `avg_processing_days`
- `supply_alert_count`, `triage_total`
- `public_health_pressure_index`
- `accreditation_risk_band`
- `denial_risk_score`
- `likely_denial_bucket`
- `review_priority`
- `model_version`, `score_run_date`

### `data/gold/gold_claims_summary.csv`

Grain: one row per service month, district, coverage program, claim type, service category, and diagnosis group.

Business purpose: claims submitted, approved, denied, pending, paid, processing time, and denial rate.

### `data/gold/gold_disbursement_summary.csv`

Grain: one row per disbursement month, district, coverage program, funding source, and payee type.

Business purpose: disbursement counts, paid/pending/failed payments, total amount, and average payment cycle days.

### `data/gold/gold_membership_summary.csv`

Grain: one row per snapshot date, district, coverage program, age group, risk segment, and chronic-condition flag.

Business purpose: member count, active members, renewal-due members, suspended members, renewals due in 60 days, and high-risk members.

### `data/gold/gold_provider_accreditation_summary.csv`

Grain: one row per facility/provider accreditation snapshot.

Business purpose: accreditation status, level, score, corrective actions, days to expiry, and accreditation risk band.

## Optional AI extension note

The current workshop version uses optional ML scoring and agent labs as the extension path. Earlier real-time and streaming artifacts are not used in the execution flow for this version.
