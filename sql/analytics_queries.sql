-- Sample analytics queries for validation, OAC datasets, or SQL worksheets.

-- 1. Facilities with the highest access risk.
SELECT
  f.district_name,
  f.facility_name,
  f.facility_type,
  ROUND(AVG(f.access_risk_score), 1) AS avg_access_risk_score,
  ROUND(AVG(f.avg_outpatient_wait_minutes), 1) AS avg_outpatient_wait,
  ROUND(AVG(f.avg_ed_wait_minutes), 1) AS avg_ed_wait,
  ROUND(AVG(f.bed_occupancy_rate), 3) AS avg_bed_occupancy
FROM mpha_gold_facility_access_daily f
GROUP BY f.district_name, f.facility_name, f.facility_type
ORDER BY avg_access_risk_score DESC
FETCH FIRST 10 ROWS ONLY;

-- 2. Weekly public-health pressure by district.
SELECT
  week_start_date,
  district_name,
  public_health_pressure_index,
  positivity_rate,
  completion_rate,
  immunization_no_show_rate,
  respiratory_related_ed_visits
FROM mpha_gold_district_public_health_weekly
ORDER BY week_start_date, public_health_pressure_index DESC;

-- 3. Capacity strain: occupancy and overtime by facility.
SELECT
  f.facility_name,
  f.facility_type,
  COUNT(CASE WHEN f.high_occupancy_flag = 'Y' THEN 1 END) AS high_occupancy_days,
  ROUND(AVG(f.bed_occupancy_rate), 3) AS avg_occupancy,
  ROUND(SUM(f.overtime_hours), 1) AS total_overtime_hours
FROM mpha_gold_facility_access_daily f
GROUP BY f.facility_name, f.facility_type
ORDER BY high_occupancy_days DESC, total_overtime_hours DESC;

-- 4. Immunization completion by district and age group.
SELECT
  district_id,
  district_name,
  age_group,
  SUM(eligible_population) AS eligible_population,
  SUM(doses_administered) AS doses_administered,
  ROUND(SUM(doses_administered) / NULLIF(SUM(eligible_population), 0), 4) AS completion_rate,
  ROUND(SUM(missed_appointments) / NULLIF(SUM(appointments_booked), 0), 4) AS no_show_rate
FROM mpha_gold_immunization_equity_weekly
GROUP BY district_id, district_name, age_group
ORDER BY district_name, age_group;

-- 5. Service-quality event closure by severity.
SELECT
  facility_name,
  severity,
  SUM(event_count) AS event_count,
  ROUND(AVG(avg_days_to_close), 1) AS avg_days_to_close,
  SUM(sla_breach_events) AS sla_breach_events
FROM mpha_gold_quality_event_summary
GROUP BY facility_name, severity
ORDER BY sla_breach_events DESC, event_count DESC;

-- 6. Respiratory pressure trend for executive dashboard.
SELECT
  week_start_date,
  district_name,
  tests_reported,
  positive_tests,
  positivity_rate,
  respiratory_related_ed_visits,
  public_health_pressure_index
FROM mpha_gold_district_public_health_weekly
WHERE positivity_rate >= 0.08
ORDER BY week_start_date, positivity_rate DESC;

-- 7. Spatial access planning insight for mobile clinic decisions.
SELECT
  district_name,
  population,
  facility_count,
  residents_per_facility,
  avg_distance_to_facility_km,
  public_health_pressure_index,
  spatial_business_insight
FROM mpha_gold_spatial_access_insights
ORDER BY residents_per_facility DESC, public_health_pressure_index DESC;

-- 8. Document-chat retrieval context for a mobile clinic prompt.
SELECT
  chunk_id,
  page_number,
  section_title,
  DBMS_LOB.SUBSTR(chunk_text, 700, 1) AS context_excerpt
FROM mpha_gold_document_chat_context
WHERE LOWER(chunk_text) LIKE '%mobile clinic%'
   OR LOWER(chunk_text) LIKE '%spatial response%'
FETCH FIRST 5 ROWS ONLY;

-- 9. Latest JSON capacity events prepared for the real-time dashboard.
SELECT
  event_timestamp,
  district_name,
  facility_name,
  current_occupancy_rate,
  waiting_room_count,
  avg_ed_wait_minutes,
  capacity_pressure_band
FROM mpha_gold_capacity_event_latest
ORDER BY event_timestamp DESC, avg_ed_wait_minutes DESC
FETCH FIRST 20 ROWS ONLY;

-- 10. Dimensional schema: facilities with highest access risk.
SELECT
  d.district_name,
  f.facility_name,
  f.facility_type,
  p.pressure_band,
  ROUND(AVG(a.access_risk_score), 1) AS avg_access_risk_score,
  ROUND(AVG(a.avg_ed_wait_minutes), 1) AS avg_ed_wait_minutes,
  ROUND(AVG(a.bed_occupancy_rate), 3) AS avg_bed_occupancy
FROM mpha_fact_facility_access_daily a
JOIN mpha_dim_facility f
  ON a.facility_key = f.facility_key
JOIN mpha_dim_district d
  ON f.district_key = d.district_key
JOIN mpha_dim_pressure_band p
  ON a.pressure_band_key = p.pressure_band_key
GROUP BY d.district_name, f.facility_name, f.facility_type, p.pressure_band
ORDER BY avg_access_risk_score DESC
FETCH FIRST 10 ROWS ONLY;

-- 11. Dimensional schema: weekly pressure with shared date and district dimensions.
SELECT
  dt.full_date AS week_start_date,
  d.district_name,
  p.pressure_band,
  ph.public_health_pressure_index,
  ph.positivity_rate,
  ph.completion_rate,
  ph.immunization_no_show_rate
FROM mpha_fact_district_public_health_weekly ph
JOIN mpha_dim_date dt
  ON ph.week_start_date_key = dt.date_key
JOIN mpha_dim_district d
  ON ph.district_key = d.district_key
JOIN mpha_dim_pressure_band p
  ON ph.pressure_band_key = p.pressure_band_key
ORDER BY dt.full_date, ph.public_health_pressure_index DESC;

-- 12. Dimensional schema: OAC-ready star view for spatial planning.
SELECT
  district_name,
  pressure_band,
  residents_per_facility,
  avg_distance_to_facility_km,
  public_health_pressure_index,
  spatial_business_insight
FROM mpha_oac_star_spatial_access
ORDER BY residents_per_facility DESC;

-- 13. Claims adjudication: denial rate and payment yield by coverage program.
SELECT
  service_month,
  district_name,
  coverage_program,
  claim_type,
  SUM(claims_submitted) AS claims_submitted,
  SUM(denied_claims) AS denied_claims,
  ROUND(SUM(denied_claims) / NULLIF(SUM(claims_submitted), 0), 4) AS denial_rate,
  ROUND(SUM(total_paid_amount) / NULLIF(SUM(total_submitted_amount), 0), 4) AS payment_yield
FROM mpha_oac_star_claims
GROUP BY service_month, district_name, coverage_program, claim_type
ORDER BY denial_rate DESC, claims_submitted DESC
FETCH FIRST 20 ROWS ONLY;

-- 14. Disbursement performance by funding source and district.
SELECT
  disbursement_month,
  district_name,
  funding_source,
  payee_type,
  SUM(disbursement_count) AS disbursement_count,
  SUM(total_disbursement_amount) AS total_disbursement_amount,
  SUM(pending_disbursements) AS pending_disbursements,
  SUM(failed_disbursements) AS failed_disbursements,
  ROUND(AVG(avg_payment_cycle_days), 1) AS avg_payment_cycle_days
FROM mpha_oac_star_disbursements
GROUP BY disbursement_month, district_name, funding_source, payee_type
ORDER BY pending_disbursements DESC, total_disbursement_amount DESC;

-- 15. Membership renewal and risk-segment view.
SELECT
  district_name,
  coverage_program,
  age_group,
  risk_segment,
  SUM(member_count) AS member_count,
  SUM(active_members) AS active_members,
  SUM(renewal_due_60_days) AS renewal_due_60_days,
  SUM(high_risk_members) AS high_risk_members
FROM mpha_oac_star_membership
GROUP BY district_name, coverage_program, age_group, risk_segment
ORDER BY renewal_due_60_days DESC, high_risk_members DESC;

-- 16. Provider accreditation oversight and corrective-action risk.
SELECT
  district_name,
  facility_name,
  facility_type,
  accreditation_status,
  accreditation_level,
  accreditation_risk_band,
  accreditation_score,
  corrective_action_count,
  days_to_expiry
FROM mpha_oac_star_provider_accreditation
ORDER BY
  CASE accreditation_risk_band WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
  corrective_action_count DESC,
  days_to_expiry ASC;
