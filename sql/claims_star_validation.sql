-- Public Healthcare AIDP Workshop
-- Claims star schema validation pack
--
-- Purpose:
-- Run these three checks after `aidp_claims_star_ai_lakehouse_pyspark.py`
-- completes successfully.
--
-- Expected outcomes:
-- 1. All five star-schema tables return non-zero row counts.
-- 2. The orphan-row check returns 0.
-- 3. The joined preview returns readable business rows for service month,
--    district, coverage program, claim type, and core claims metrics.

-- ============================================================
-- 1. Row counts
-- ============================================================
select 'mpha_dim_date' as table_name, count(*) as row_count from mpha_dim_date
union all
select 'mpha_dim_district', count(*) from mpha_dim_district
union all
select 'mpha_dim_coverage_program', count(*) from mpha_dim_coverage_program
union all
select 'mpha_dim_claim_type', count(*) from mpha_dim_claim_type
union all
select 'mpha_fact_claims_monthly', count(*) from mpha_fact_claims_monthly
order by 1;


-- ============================================================
-- 2. Orphan join check
-- Expected: ORPHAN_ROWS = 0
-- ============================================================
select count(*) as orphan_rows
from mpha_fact_claims_monthly f
left join mpha_dim_date d
  on f.service_month_date_key = d.date_key
left join mpha_dim_district di
  on f.district_key = di.district_key
left join mpha_dim_coverage_program p
  on f.program_key = p.program_key
left join mpha_dim_claim_type c
  on f.claim_type_key = c.claim_type_key
where d.date_key is null
   or di.district_key is null
   or p.program_key is null
   or c.claim_type_key is null;


-- ============================================================
-- 3. Joined preview
-- Expected: readable business rows with populated measures
-- ============================================================
select
  d.full_date as service_month,
  di.district_name,
  p.coverage_program,
  c.claim_type,
  f.claims_submitted,
  f.approved_claims,
  f.denied_claims,
  f.pending_claims,
  f.total_submitted_amount,
  f.total_paid_amount,
  f.avg_processing_days,
  f.denial_rate
from mpha_fact_claims_monthly f
join mpha_dim_date d
  on f.service_month_date_key = d.date_key
join mpha_dim_district di
  on f.district_key = di.district_key
join mpha_dim_coverage_program p
  on f.program_key = p.program_key
join mpha_dim_claim_type c
  on f.claim_type_key = c.claim_type_key
order by d.full_date, di.district_name
fetch first 20 rows only;
