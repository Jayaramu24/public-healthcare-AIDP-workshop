-- Public Healthcare AIDP Workshop
-- Admin setup: prepare participant AI Lakehouse schemas for AIDP Claims star schema loads.
--
-- Run this script as ADMIN in Autonomous AI Lakehouse Database Actions.
-- It creates the Claims star schema tables in MPHA_P01 through MPHA_P17 if missing,
-- gives each participant quota on DATA, and grants the AIDP external catalog user
-- SELECT and INSERT so AIDP Spark notebooks can publish Gold tables.
--
-- Adjust these values if your workshop uses different participant user names or
-- a different AIDP external catalog database user.

set define off

declare
  c_participant_count constant pls_integer := 17;
  c_aidp_catalog_user constant varchar2(128) := 'E2EAIDPUSER';
  l_schema varchar2(128);

  procedure create_if_missing(p_sql in varchar2) is
  begin
    execute immediate p_sql;
  exception
    when others then
      if sqlcode = -955 then
        null;
      else
        raise;
      end if;
  end;

  procedure grant_if_possible(p_sql in varchar2) is
  begin
    execute immediate p_sql;
  exception
    when others then
      if sqlcode in (-1917, -942) then
        dbms_output.put_line('Grant skipped: ' || p_sql || ' - ' || sqlerrm);
      else
        raise;
      end if;
  end;

begin
  for i in 1..c_participant_count loop
    l_schema := 'MPHA_P' || lpad(i, 2, '0');

    execute immediate 'alter user ' || l_schema || ' quota 1G on DATA';

    create_if_missing('create table ' || l_schema || '.mpha_dim_date (
      date_key number primary key,
      full_date date,
      calendar_year number,
      calendar_quarter number,
      month_number number,
      month_name varchar2(20),
      week_start_date date,
      day_of_week varchar2(20),
      is_week_start varchar2(1)
    )');

    create_if_missing('create table ' || l_schema || '.mpha_dim_district (
      district_key number primary key,
      district_id varchar2(10),
      district_name varchar2(80),
      population number,
      deprivation_index number,
      elderly_pct number,
      chronic_condition_pct number,
      median_income_usd number
    )');

    create_if_missing('create table ' || l_schema || '.mpha_dim_coverage_program (
      program_key number primary key,
      program_code varchar2(12),
      coverage_program varchar2(80),
      program_type varchar2(80),
      funding_source varchar2(100)
    )');

    create_if_missing('create table ' || l_schema || '.mpha_dim_claim_type (
      claim_type_key number primary key,
      claim_type varchar2(40),
      service_category varchar2(80),
      diagnosis_group varchar2(80)
    )');

    create_if_missing('create table ' || l_schema || '.mpha_fact_claims_monthly (
      service_month_date_key number,
      district_key number,
      program_key number,
      claim_type_key number,
      claims_submitted number,
      approved_claims number,
      denied_claims number,
      pending_claims number,
      total_submitted_amount number,
      total_approved_amount number,
      total_paid_amount number,
      avg_processing_days number,
      denial_rate number
    )');

    execute immediate 'create or replace view ' || l_schema || '.mpha_oac_star_claims as
      select
        d.full_date as service_month,
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
      from ' || l_schema || '.mpha_fact_claims_monthly f
      join ' || l_schema || '.mpha_dim_date d
        on f.service_month_date_key = d.date_key
      join ' || l_schema || '.mpha_dim_district dis
        on f.district_key = dis.district_key
      join ' || l_schema || '.mpha_dim_coverage_program p
        on f.program_key = p.program_key
      join ' || l_schema || '.mpha_dim_claim_type ct
        on f.claim_type_key = ct.claim_type_key';

    grant_if_possible('grant select, insert on ' || l_schema || '.mpha_dim_date to ' || c_aidp_catalog_user);
    grant_if_possible('grant select, insert on ' || l_schema || '.mpha_dim_district to ' || c_aidp_catalog_user);
    grant_if_possible('grant select, insert on ' || l_schema || '.mpha_dim_coverage_program to ' || c_aidp_catalog_user);
    grant_if_possible('grant select, insert on ' || l_schema || '.mpha_dim_claim_type to ' || c_aidp_catalog_user);
    grant_if_possible('grant select, insert on ' || l_schema || '.mpha_fact_claims_monthly to ' || c_aidp_catalog_user);
    grant_if_possible('grant select on ' || l_schema || '.mpha_oac_star_claims to ' || c_aidp_catalog_user);

    dbms_output.put_line(l_schema || ' ready for AIDP Claims star schema load.');
  end loop;
end;
/

select owner, table_name
from all_tables
where owner like 'MPHA_P__'
  and table_name in (
    'MPHA_DIM_DATE',
    'MPHA_DIM_DISTRICT',
    'MPHA_DIM_COVERAGE_PROGRAM',
    'MPHA_DIM_CLAIM_TYPE',
    'MPHA_FACT_CLAIMS_MONTHLY'
  )
order by owner, table_name;

select grantee, owner, table_name, privilege
from dba_tab_privs
where grantee = 'E2EAIDPUSER'
  and owner like 'MPHA_P__'
  and table_name in (
    'MPHA_DIM_DATE',
    'MPHA_DIM_DISTRICT',
    'MPHA_DIM_COVERAGE_PROGRAM',
    'MPHA_DIM_CLAIM_TYPE',
    'MPHA_FACT_CLAIMS_MONTHLY',
    'MPHA_OAC_STAR_CLAIMS'
  )
order by owner, table_name, privilege;
