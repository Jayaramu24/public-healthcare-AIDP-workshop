-- Public Healthcare Lakehouse Analytics Workshop
-- Flat AI Lakehouse Gold mart setup
--
-- NOTE: The recommended workshop Gold model is the dimensional snowflake
-- schema in sql/create_ai_lakehouse_dimensional_gold_schema.sql. This file is
-- retained as a simpler flat-mart compatibility path for validation and
-- comparison.
--
-- Gold is the business serving layer. AIDP stages Gold outputs under:
--   oci://<bucket>@<namespace>/mpha/gold_stage/<gold_object_name>/
--
-- Replace <gold_stage_uri> with the object storage URI that contains the
-- AIDP-generated Gold CSV folders, then run these statements in Autonomous AI
-- Lakehouse or Autonomous Data Warehouse.

CREATE TABLE mpha_gold_facility_access_daily (
  service_date DATE,
  facility_id VARCHAR2(10),
  facility_name VARCHAR2(120),
  facility_type VARCHAR2(40),
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
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

CREATE TABLE mpha_gold_district_public_health_weekly (
  week_start_date DATE,
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
  district_population NUMBER,
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

CREATE TABLE mpha_gold_immunization_equity_weekly (
  week_start_date DATE,
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
  age_group VARCHAR2(10),
  eligible_population NUMBER,
  appointments_booked NUMBER,
  missed_appointments NUMBER,
  walk_in_visits NUMBER,
  doses_administered NUMBER,
  completion_rate NUMBER,
  immunization_no_show_rate NUMBER,
  deprivation_index NUMBER,
  elderly_pct NUMBER
);

CREATE TABLE mpha_gold_quality_event_summary (
  facility_id VARCHAR2(10),
  facility_name VARCHAR2(120),
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
  severity VARCHAR2(20),
  event_type VARCHAR2(80),
  event_count NUMBER,
  avg_days_to_close NUMBER,
  sla_breach_events NUMBER,
  avoidable_readmission_events NUMBER
);

CREATE TABLE mpha_gold_executive_overview (
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
  total_outpatient_visits NUMBER,
  total_emergency_arrivals NUMBER,
  avg_ed_wait_minutes NUMBER,
  avg_outpatient_wait_minutes NUMBER,
  avg_bed_occupancy_rate NUMBER,
  high_occupancy_days NUMBER,
  total_overtime_hours NUMBER,
  avg_access_risk_score NUMBER
);

CREATE TABLE mpha_gold_spatial_access_insights (
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
  population NUMBER,
  facility_count NUMBER,
  residents_per_facility NUMBER,
  avg_distance_to_facility_km NUMBER,
  public_health_pressure_index NUMBER,
  high_pressure_facilities VARCHAR2(1000),
  spatial_business_insight VARCHAR2(500)
);

CREATE TABLE mpha_gold_capacity_event_latest (
  event_timestamp TIMESTAMP,
  facility_id VARCHAR2(10),
  facility_name VARCHAR2(120),
  district_id VARCHAR2(10),
  district_name VARCHAR2(80),
  current_occupancy_rate NUMBER,
  waiting_room_count NUMBER,
  avg_ed_wait_minutes NUMBER,
  triage_total NUMBER,
  supply_alert_count NUMBER,
  ambulance_diversion_status VARCHAR2(8),
  capacity_pressure_band VARCHAR2(20)
);

CREATE TABLE mpha_gold_document_chat_context (
  document_id VARCHAR2(80),
  chunk_id VARCHAR2(120),
  page_number NUMBER,
  section_title VARCHAR2(240),
  chunk_text CLOB,
  embedding_model VARCHAR2(80),
  embedding_json CLOB
);

CREATE TABLE mpha_gold_claims_summary (
  service_month DATE,
  district_id VARCHAR2(10),
  program_code VARCHAR2(12),
  coverage_program VARCHAR2(80),
  claim_type VARCHAR2(40),
  service_category VARCHAR2(80),
  diagnosis_group VARCHAR2(80),
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

CREATE TABLE mpha_gold_disbursement_summary (
  disbursement_month DATE,
  district_id VARCHAR2(10),
  program_code VARCHAR2(12),
  coverage_program VARCHAR2(80),
  funding_source VARCHAR2(100),
  payee_type VARCHAR2(60),
  disbursement_count NUMBER,
  paid_disbursements NUMBER,
  pending_disbursements NUMBER,
  failed_disbursements NUMBER,
  total_disbursement_amount NUMBER,
  avg_payment_cycle_days NUMBER
);

CREATE TABLE mpha_gold_membership_summary (
  snapshot_date DATE,
  district_id VARCHAR2(10),
  program_code VARCHAR2(12),
  coverage_program VARCHAR2(80),
  age_group VARCHAR2(20),
  risk_segment VARCHAR2(20),
  chronic_condition_flag VARCHAR2(1),
  member_count NUMBER,
  active_members NUMBER,
  renewal_due_members NUMBER,
  suspended_members NUMBER,
  renewal_due_60_days NUMBER,
  high_risk_members NUMBER
);

CREATE TABLE mpha_gold_provider_accreditation_summary (
  provider_id VARCHAR2(20),
  facility_id VARCHAR2(10),
  provider_name VARCHAR2(120),
  district_id VARCHAR2(10),
  facility_type VARCHAR2(40),
  accreditation_body VARCHAR2(120),
  accreditation_status VARCHAR2(40),
  accreditation_level VARCHAR2(40),
  last_survey_date DATE,
  expiry_date DATE,
  accreditation_score NUMBER,
  corrective_action_count NUMBER,
  specialty_scope VARCHAR2(500),
  snapshot_date DATE,
  days_to_expiry NUMBER,
  accreditation_risk_band VARCHAR2(20)
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

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_FACILITY_ACCESS_DAILY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_facility_access_daily/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_DISTRICT_PUBLIC_HEALTH_WEEKLY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_district_public_health_weekly/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_IMMUNIZATION_EQUITY_WEEKLY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_immunization_equity_weekly/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_QUALITY_EVENT_SUMMARY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_quality_event_summary/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_EXECUTIVE_OVERVIEW',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_executive_overview/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_SPATIAL_ACCESS_INSIGHTS',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_spatial_access_insights/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_CAPACITY_EVENT_LATEST',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_capacity_event_latest/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'timestampformat' VALUE 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_DOCUMENT_CHAT_CONTEXT',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_document_chat_context/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_CLAIMS_SUMMARY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_claims_summary/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_DISBURSEMENT_SUMMARY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_disbursement_summary/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_MEMBERSHIP_SUMMARY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_membership_summary/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD')
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'MPHA_GOLD_PROVIDER_ACCREDITATION_SUMMARY',
    credential_name => 'OBJ_STORE_CRED',
    file_uri_list   => '<gold_stage_uri>/gold_provider_accreditation_summary/*.csv',
    format          => JSON_OBJECT('type' VALUE 'csv', 'skipheaders' VALUE '1', 'dateformat' VALUE 'YYYY-MM-DD')
  );
END;
/

CREATE OR REPLACE VIEW mpha_oac_executive_overview AS
SELECT
  e.district_id,
  e.district_name,
  e.total_outpatient_visits,
  e.total_emergency_arrivals,
  e.avg_ed_wait_minutes,
  e.avg_outpatient_wait_minutes,
  e.avg_bed_occupancy_rate,
  e.high_occupancy_days,
  e.total_overtime_hours,
  e.avg_access_risk_score,
  p.public_health_pressure_index,
  p.completion_rate,
  p.positivity_rate
FROM mpha_gold_executive_overview e
LEFT JOIN (
  SELECT
    district_id,
    MAX(public_health_pressure_index) AS public_health_pressure_index,
    AVG(completion_rate) AS completion_rate,
    AVG(positivity_rate) AS positivity_rate
  FROM mpha_gold_district_public_health_weekly
  GROUP BY district_id
) p
  ON e.district_id = p.district_id;

CREATE OR REPLACE VIEW mpha_oac_access_capacity AS
SELECT
  service_date,
  district_name,
  facility_name,
  facility_type,
  outpatient_visits,
  emergency_arrivals,
  avg_ed_wait_minutes,
  avg_outpatient_wait_minutes,
  bed_occupancy_rate,
  high_occupancy_flag,
  overtime_hours,
  patient_satisfaction_score,
  access_risk_score
FROM mpha_gold_facility_access_daily;

CREATE OR REPLACE VIEW mpha_oac_public_health_pressure AS
SELECT
  week_start_date,
  district_id,
  district_name,
  district_population,
  doses_administered,
  completion_rate,
  immunization_no_show_rate,
  positivity_rate,
  respiratory_related_ed_visits,
  public_health_pressure_index
FROM mpha_gold_district_public_health_weekly;

CREATE OR REPLACE VIEW mpha_oac_spatial_access AS
SELECT
  district_id,
  district_name,
  population,
  facility_count,
  residents_per_facility,
  avg_distance_to_facility_km,
  public_health_pressure_index,
  high_pressure_facilities,
  spatial_business_insight
FROM mpha_gold_spatial_access_insights;

CREATE OR REPLACE VIEW mpha_oac_capacity_event_latest AS
SELECT
  event_timestamp,
  facility_id,
  facility_name,
  district_id,
  district_name,
  current_occupancy_rate,
  waiting_room_count,
  avg_ed_wait_minutes,
  triage_total,
  supply_alert_count,
  ambulance_diversion_status,
  capacity_pressure_band
FROM mpha_gold_capacity_event_latest;

CREATE OR REPLACE VIEW mpha_oac_document_chat_context AS
SELECT
  document_id,
  chunk_id,
  page_number,
  section_title,
  chunk_text,
  embedding_model,
  embedding_json
FROM mpha_gold_document_chat_context;
