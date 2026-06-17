-- Public Healthcare AIDP Workshop
-- Recommended AI Lakehouse Gold dimensional schema
--
-- Shape: snowflake / fact constellation.
-- Shared dimensions are reused across multiple facts. Facility snowflakes to
-- District through DIM_FACILITY.DISTRICT_KEY, while district-grain facts join
-- directly to DIM_DISTRICT. This gives OAC a stable semantic layer while
-- keeping the original flat Gold marts available as compatibility samples.
--
-- AIDP stages dimensional Gold outputs under:
--   oci://<bucket>@<namespace>/mpha/gold_dimensional/<object_name>/
--
-- Replace <gold_dimensional_stage_uri> with that object storage URI.

-- ============================================================
-- Dimensions
-- ============================================================

CREATE TABLE mpha_dim_date (
  date_key NUMBER PRIMARY KEY,
  full_date DATE,
  calendar_year NUMBER,
  calendar_quarter NUMBER,
  month_number NUMBER,
  month_name VARCHAR2(20),
  week_start_date DATE,
  day_of_week VARCHAR2(20),
  is_week_start VARCHAR2(1)
);

CREATE TABLE mpha_dim_district (
  district_key NUMBER PRIMARY KEY,
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
  population NUMBER,
  deprivation_index NUMBER,
  elderly_pct NUMBER,
  chronic_condition_pct NUMBER,
  median_income_usd NUMBER
);

CREATE TABLE mpha_dim_facility (
  facility_key NUMBER PRIMARY KEY,
  facility_id VARCHAR2(10),
  facility_name VARCHAR2(120),
  facility_type VARCHAR2(40),
  district_key NUMBER,
  district_id VARCHAR2(10),
  latitude NUMBER,
  longitude NUMBER,
  licensed_beds NUMBER,
  baseline_daily_visits NUMBER,
  target_ed_wait_minutes NUMBER,
  target_outpatient_wait_minutes NUMBER
);

CREATE TABLE mpha_dim_age_group (
  age_group_key NUMBER PRIMARY KEY,
  age_group VARCHAR2(20),
  sort_order NUMBER
);

CREATE TABLE mpha_dim_quality_event (
  quality_event_key NUMBER PRIMARY KEY,
  event_type VARCHAR2(80),
  severity VARCHAR2(20)
);

CREATE TABLE mpha_dim_pressure_band (
  pressure_band_key NUMBER PRIMARY KEY,
  pressure_band VARCHAR2(20),
  lower_bound NUMBER,
  upper_bound NUMBER,
  description VARCHAR2(160)
);

CREATE TABLE mpha_dim_document_chunk (
  document_chunk_key NUMBER PRIMARY KEY,
  document_id VARCHAR2(80),
  chunk_id VARCHAR2(120),
  page_number NUMBER,
  section_title VARCHAR2(240),
  chunk_text CLOB,
  embedding_model VARCHAR2(80),
  embedding_json CLOB
);

CREATE TABLE mpha_dim_coverage_program (
  program_key NUMBER PRIMARY KEY,
  program_code VARCHAR2(12),
  coverage_program VARCHAR2(80),
  program_type VARCHAR2(80),
  funding_source VARCHAR2(100)
);

CREATE TABLE mpha_dim_claim_type (
  claim_type_key NUMBER PRIMARY KEY,
  claim_type VARCHAR2(40),
  service_category VARCHAR2(80),
  diagnosis_group VARCHAR2(80)
);

CREATE TABLE mpha_dim_member_segment (
  member_segment_key NUMBER PRIMARY KEY,
  age_group VARCHAR2(20),
  risk_segment VARCHAR2(20),
  chronic_condition_flag VARCHAR2(1)
);

CREATE TABLE mpha_dim_accreditation_status (
  accreditation_status_key NUMBER PRIMARY KEY,
  accreditation_body VARCHAR2(120),
  accreditation_status VARCHAR2(40),
  accreditation_level VARCHAR2(40),
  specialty_scope VARCHAR2(500)
);

-- ============================================================
-- Facts
-- ============================================================

CREATE TABLE mpha_fact_facility_access_daily (
  date_key NUMBER,
  facility_key NUMBER,
  pressure_band_key NUMBER,
  outpatient_visits NUMBER,
  emergency_arrivals NUMBER,
  admissions NUMBER,
  discharges NUMBER,
  avg_ed_wait_minutes NUMBER,
  avg_outpatient_wait_minutes NUMBER,
  ed_wait_variance_minutes NUMBER,
  outpatient_wait_variance_minutes NUMBER,
  bed_occupancy_rate NUMBER,
  high_occupancy_flag VARCHAR2(1),
  staff_hours NUMBER,
  overtime_hours NUMBER,
  patient_satisfaction_score NUMBER,
  access_risk_score NUMBER
);

CREATE TABLE mpha_fact_district_public_health_weekly (
  week_start_date_key NUMBER,
  district_key NUMBER,
  pressure_band_key NUMBER,
  eligible_population NUMBER,
  appointments_booked NUMBER,
  missed_appointments NUMBER,
  doses_administered NUMBER,
  completion_rate NUMBER,
  immunization_no_show_rate NUMBER,
  tests_reported NUMBER,
  positive_tests NUMBER,
  positivity_rate NUMBER,
  respiratory_related_ed_visits NUMBER,
  public_health_pressure_index NUMBER
);

CREATE TABLE mpha_fact_immunization_equity_weekly (
  week_start_date_key NUMBER,
  district_key NUMBER,
  age_group_key NUMBER,
  eligible_population NUMBER,
  appointments_booked NUMBER,
  missed_appointments NUMBER,
  walk_in_visits NUMBER,
  doses_administered NUMBER,
  completion_rate NUMBER,
  immunization_no_show_rate NUMBER
);

CREATE TABLE mpha_fact_quality_event_summary (
  facility_key NUMBER,
  quality_event_key NUMBER,
  event_count NUMBER,
  avg_days_to_close NUMBER,
  sla_breach_events NUMBER,
  avoidable_readmission_events NUMBER
);

CREATE TABLE mpha_fact_spatial_access_insight (
  district_key NUMBER,
  pressure_band_key NUMBER,
  facility_count NUMBER,
  residents_per_facility NUMBER,
  avg_distance_to_facility_km NUMBER,
  public_health_pressure_index NUMBER,
  high_pressure_facilities VARCHAR2(1000),
  spatial_business_insight VARCHAR2(500)
);

CREATE TABLE mpha_fact_capacity_event (
  event_date_key NUMBER,
  event_timestamp TIMESTAMP,
  facility_key NUMBER,
  pressure_band_key NUMBER,
  current_occupancy_rate NUMBER,
  waiting_room_count NUMBER,
  avg_ed_wait_minutes NUMBER,
  triage_total NUMBER,
  supply_alert_count NUMBER,
  ambulance_diversion_status VARCHAR2(8)
);

CREATE TABLE mpha_fact_stream_wait_time_minute (
  event_date_key NUMBER,
  event_minute TIMESTAMP,
  facility_key NUMBER,
  pressure_band_key NUMBER,
  avg_wait_minutes NUMBER,
  max_wait_minutes NUMBER,
  avg_occupancy_rate NUMBER,
  max_queue_depth NUMBER,
  event_count NUMBER
);

CREATE TABLE mpha_bridge_chat_topic_chunk (
  chat_topic_key NUMBER,
  question VARCHAR2(500),
  structured_context VARCHAR2(240),
  document_chunk_key NUMBER,
  relevance_rank NUMBER,
  sample_answer CLOB
);

CREATE TABLE mpha_fact_claims_monthly (
  service_month_date_key NUMBER,
  district_key NUMBER,
  program_key NUMBER,
  claim_type_key NUMBER,
  claims_submitted NUMBER,
  approved_claims NUMBER,
  denied_claims NUMBER,
  pending_claims NUMBER,
  total_submitted_amount NUMBER,
  total_approved_amount NUMBER,
  total_paid_amount NUMBER,
  avg_processing_days NUMBER,
  denial_rate NUMBER
);

CREATE TABLE mpha_fact_disbursement_monthly (
  disbursement_month_date_key NUMBER,
  district_key NUMBER,
  program_key NUMBER,
  payee_type VARCHAR2(60),
  disbursement_count NUMBER,
  paid_disbursements NUMBER,
  pending_disbursements NUMBER,
  failed_disbursements NUMBER,
  total_disbursement_amount NUMBER,
  avg_payment_cycle_days NUMBER
);

CREATE TABLE mpha_fact_membership_snapshot (
  snapshot_date_key NUMBER,
  district_key NUMBER,
  program_key NUMBER,
  member_segment_key NUMBER,
  member_count NUMBER,
  active_members NUMBER,
  renewal_due_members NUMBER,
  suspended_members NUMBER,
  renewal_due_60_days NUMBER,
  high_risk_members NUMBER
);

CREATE TABLE mpha_fact_provider_accreditation (
  snapshot_date_key NUMBER,
  last_survey_date_key NUMBER,
  expiry_date_key NUMBER,
  facility_key NUMBER,
  accreditation_status_key NUMBER,
  pressure_band_key NUMBER,
  provider_id VARCHAR2(20),
  accreditation_score NUMBER,
  corrective_action_count NUMBER,
  days_to_expiry NUMBER
);

-- Optional: create a credential once if loading from Object Storage.
-- BEGIN
--   DBMS_CLOUD.CREATE_CREDENTIAL(
--     credential_name => 'OBJ_STORE_CRED',
--     username        => '<oci_user>',
--     password        => '<auth_token>'
--   );
-- END;
-- /

-- ============================================================
-- Load dimensions and facts
-- ============================================================

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_DATE', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_date/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_DISTRICT', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_district/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_FACILITY', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_facility/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_AGE_GROUP', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_age_group/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_QUALITY_EVENT', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_quality_event/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_PRESSURE_BAND', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_pressure_band/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_DOCUMENT_CHUNK', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_document_chunk/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_COVERAGE_PROGRAM', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_coverage_program/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_CLAIM_TYPE', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_claim_type/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_MEMBER_SEGMENT', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_member_segment/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_DIM_ACCREDITATION_STATUS', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/dim_accreditation_status/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_FACILITY_ACCESS_DAILY', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_facility_access_daily/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_DISTRICT_PUBLIC_HEALTH_WEEKLY', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_district_public_health_weekly/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_IMMUNIZATION_EQUITY_WEEKLY', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_immunization_equity_weekly/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_QUALITY_EVENT_SUMMARY', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_quality_event_summary/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_SPATIAL_ACCESS_INSIGHT', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_spatial_access_insight/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_CAPACITY_EVENT', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_capacity_event/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'timestampformat' VALUE 'YYYY-MM-DD"T"HH24:MI:SS"Z"'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_STREAM_WAIT_TIME_MINUTE', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_stream_wait_time_minute/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'timestampformat' VALUE 'YYYY-MM-DD"T"HH24:MI:SS"Z"'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_BRIDGE_CHAT_TOPIC_CHUNK', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/bridge_chat_topic_chunk/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_CLAIMS_MONTHLY', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_claims_monthly/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_DISBURSEMENT_MONTHLY', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_disbursement_monthly/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_MEMBERSHIP_SNAPSHOT', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_membership_snapshot/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(table_name => 'MPHA_FACT_PROVIDER_ACCREDITATION', credential_name => 'OBJ_STORE_CRED',
    file_uri_list => '<gold_dimensional_stage_uri>/fact_provider_accreditation/*.csv',
    format => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1'));
END;
/

-- ============================================================
-- OAC semantic views over the dimensional model
-- ============================================================

CREATE OR REPLACE VIEW mpha_oac_star_access_capacity AS
SELECT
  d.full_date AS service_date,
  d.calendar_year,
  d.month_name,
  dis.district_id,
  dis.district_name,
  fac.facility_id,
  fac.facility_name,
  fac.facility_type,
  pb.pressure_band,
  f.outpatient_visits,
  f.emergency_arrivals,
  f.admissions,
  f.discharges,
  f.avg_ed_wait_minutes,
  f.avg_outpatient_wait_minutes,
  f.ed_wait_variance_minutes,
  f.outpatient_wait_variance_minutes,
  f.bed_occupancy_rate,
  f.high_occupancy_flag,
  f.staff_hours,
  f.overtime_hours,
  f.patient_satisfaction_score,
  f.access_risk_score
FROM mpha_fact_facility_access_daily f
JOIN mpha_dim_date d ON f.date_key = d.date_key
JOIN mpha_dim_facility fac ON f.facility_key = fac.facility_key
JOIN mpha_dim_district dis ON fac.district_key = dis.district_key
JOIN mpha_dim_pressure_band pb ON f.pressure_band_key = pb.pressure_band_key;

CREATE OR REPLACE VIEW mpha_oac_star_public_health_pressure AS
SELECT
  d.full_date AS week_start_date,
  dis.district_id,
  dis.district_name,
  dis.population AS district_population,
  pb.pressure_band,
  f.eligible_population,
  f.appointments_booked,
  f.missed_appointments,
  f.doses_administered,
  f.completion_rate,
  f.immunization_no_show_rate,
  f.tests_reported,
  f.positive_tests,
  f.positivity_rate,
  f.respiratory_related_ed_visits,
  f.public_health_pressure_index
FROM mpha_fact_district_public_health_weekly f
JOIN mpha_dim_date d ON f.week_start_date_key = d.date_key
JOIN mpha_dim_district dis ON f.district_key = dis.district_key
JOIN mpha_dim_pressure_band pb ON f.pressure_band_key = pb.pressure_band_key;

CREATE OR REPLACE VIEW mpha_oac_star_immunization_equity AS
SELECT
  d.full_date AS week_start_date,
  dis.district_id,
  dis.district_name,
  age.age_group,
  age.sort_order AS age_group_sort,
  f.eligible_population,
  f.appointments_booked,
  f.missed_appointments,
  f.walk_in_visits,
  f.doses_administered,
  f.completion_rate,
  f.immunization_no_show_rate
FROM mpha_fact_immunization_equity_weekly f
JOIN mpha_dim_date d ON f.week_start_date_key = d.date_key
JOIN mpha_dim_district dis ON f.district_key = dis.district_key
JOIN mpha_dim_age_group age ON f.age_group_key = age.age_group_key;

CREATE OR REPLACE VIEW mpha_oac_star_quality_events AS
SELECT
  dis.district_id,
  dis.district_name,
  fac.facility_id,
  fac.facility_name,
  fac.facility_type,
  qe.event_type,
  qe.severity,
  f.event_count,
  f.avg_days_to_close,
  f.sla_breach_events,
  f.avoidable_readmission_events
FROM mpha_fact_quality_event_summary f
JOIN mpha_dim_facility fac ON f.facility_key = fac.facility_key
JOIN mpha_dim_district dis ON fac.district_key = dis.district_key
JOIN mpha_dim_quality_event qe ON f.quality_event_key = qe.quality_event_key;

CREATE OR REPLACE VIEW mpha_oac_star_spatial_access AS
SELECT
  dis.district_id,
  dis.district_name,
  dis.population,
  pb.pressure_band,
  f.facility_count,
  f.residents_per_facility,
  f.avg_distance_to_facility_km,
  f.public_health_pressure_index,
  f.high_pressure_facilities,
  f.spatial_business_insight
FROM mpha_fact_spatial_access_insight f
JOIN mpha_dim_district dis ON f.district_key = dis.district_key
JOIN mpha_dim_pressure_band pb ON f.pressure_band_key = pb.pressure_band_key;

CREATE OR REPLACE VIEW mpha_oac_star_realtime_operations AS
SELECT
  f.event_timestamp,
  dis.district_id,
  dis.district_name,
  fac.facility_id,
  fac.facility_name,
  fac.facility_type,
  pb.pressure_band,
  f.current_occupancy_rate,
  f.waiting_room_count,
  f.avg_ed_wait_minutes,
  f.triage_total,
  f.supply_alert_count,
  f.ambulance_diversion_status
FROM mpha_fact_capacity_event f
JOIN mpha_dim_facility fac ON f.facility_key = fac.facility_key
JOIN mpha_dim_district dis ON fac.district_key = dis.district_key
JOIN mpha_dim_pressure_band pb ON f.pressure_band_key = pb.pressure_band_key;

CREATE OR REPLACE VIEW mpha_oac_star_document_chat_context AS
SELECT
  b.chat_topic_key,
  b.question,
  b.structured_context,
  b.relevance_rank,
  b.sample_answer,
  c.document_id,
  c.chunk_id,
  c.page_number,
  c.section_title,
  c.chunk_text,
  c.embedding_model,
  c.embedding_json
FROM mpha_bridge_chat_topic_chunk b
JOIN mpha_dim_document_chunk c ON b.document_chunk_key = c.document_chunk_key;

CREATE OR REPLACE VIEW mpha_oac_star_claims AS
SELECT
  d.full_date AS service_month,
  dis.district_id,
  dis.district_name,
  p.program_code,
  p.coverage_program,
  p.program_type,
  p.funding_source,
  ct.claim_type,
  ct.service_category,
  ct.diagnosis_group,
  f.claims_submitted,
  f.approved_claims,
  f.denied_claims,
  f.pending_claims,
  f.total_submitted_amount,
  f.total_approved_amount,
  f.total_paid_amount,
  f.avg_processing_days,
  f.denial_rate
FROM mpha_fact_claims_monthly f
JOIN mpha_dim_date d ON f.service_month_date_key = d.date_key
JOIN mpha_dim_district dis ON f.district_key = dis.district_key
JOIN mpha_dim_coverage_program p ON f.program_key = p.program_key
JOIN mpha_dim_claim_type ct ON f.claim_type_key = ct.claim_type_key;

CREATE OR REPLACE VIEW mpha_oac_star_disbursements AS
SELECT
  d.full_date AS disbursement_month,
  dis.district_id,
  dis.district_name,
  p.program_code,
  p.coverage_program,
  p.program_type,
  p.funding_source,
  f.payee_type,
  f.disbursement_count,
  f.paid_disbursements,
  f.pending_disbursements,
  f.failed_disbursements,
  f.total_disbursement_amount,
  f.avg_payment_cycle_days
FROM mpha_fact_disbursement_monthly f
JOIN mpha_dim_date d ON f.disbursement_month_date_key = d.date_key
JOIN mpha_dim_district dis ON f.district_key = dis.district_key
JOIN mpha_dim_coverage_program p ON f.program_key = p.program_key;

CREATE OR REPLACE VIEW mpha_oac_star_membership AS
SELECT
  d.full_date AS snapshot_date,
  dis.district_id,
  dis.district_name,
  p.program_code,
  p.coverage_program,
  p.program_type,
  p.funding_source,
  ms.age_group,
  ms.risk_segment,
  ms.chronic_condition_flag,
  f.member_count,
  f.active_members,
  f.renewal_due_members,
  f.suspended_members,
  f.renewal_due_60_days,
  f.high_risk_members
FROM mpha_fact_membership_snapshot f
JOIN mpha_dim_date d ON f.snapshot_date_key = d.date_key
JOIN mpha_dim_district dis ON f.district_key = dis.district_key
JOIN mpha_dim_coverage_program p ON f.program_key = p.program_key
JOIN mpha_dim_member_segment ms ON f.member_segment_key = ms.member_segment_key;

CREATE OR REPLACE VIEW mpha_oac_star_provider_accreditation AS
SELECT
  snap.full_date AS snapshot_date,
  survey.full_date AS last_survey_date,
  expiry.full_date AS expiry_date,
  dis.district_id,
  dis.district_name,
  fac.facility_id,
  fac.facility_name,
  fac.facility_type,
  acc.accreditation_body,
  acc.accreditation_status,
  acc.accreditation_level,
  acc.specialty_scope,
  pb.pressure_band AS accreditation_risk_band,
  f.provider_id,
  f.accreditation_score,
  f.corrective_action_count,
  f.days_to_expiry
FROM mpha_fact_provider_accreditation f
JOIN mpha_dim_date snap ON f.snapshot_date_key = snap.date_key
JOIN mpha_dim_date survey ON f.last_survey_date_key = survey.date_key
JOIN mpha_dim_date expiry ON f.expiry_date_key = expiry.date_key
JOIN mpha_dim_facility fac ON f.facility_key = fac.facility_key
JOIN mpha_dim_district dis ON fac.district_key = dis.district_key
JOIN mpha_dim_accreditation_status acc ON f.accreditation_status_key = acc.accreditation_status_key
JOIN mpha_dim_pressure_band pb ON f.pressure_band_key = pb.pressure_band_key;
