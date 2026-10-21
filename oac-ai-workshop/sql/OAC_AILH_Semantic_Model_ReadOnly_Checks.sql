-- Healthcare workshop semantic model preparation
-- Connection: MaxicareWorkshop
-- Schema: ORIGAMI_ADMIN02
-- Read-only catalog and aggregate checks; no DDL or DML.
-- Executed through OAC Manual Query on 19 October 2026.
-- Run one statement at a time. Omit its trailing semicolon in the OAC editor.
-- Results below are a dated source snapshot. Re-run before workshop delivery.

-- 1. Source column inventory
SELECT
    TABLE_NAME,
    LISTAGG(COLUMN_NAME || ' ' || DATA_TYPE, ', ')
        WITHIN GROUP (ORDER BY COLUMN_ID) AS COLUMN_SPEC
FROM ALL_TAB_COLUMNS
WHERE OWNER = 'ORIGAMI_ADMIN02'
  AND TABLE_NAME IN (
      'MPHA_FACT_CLAIMS_MONTHLY',
      'MPHA_DIM_DATE',
      'MPHA_DIM_DISTRICT',
      'MPHA_DIM_COVERAGE_PROGRAM',
      'MPHA_DIM_CLAIM_TYPE',
      'MPHA_OAC_STAR_CLAIMS',
      'MPHA_FACT_DISTRICT_CLAIMS_CONTEXT'
  )
GROUP BY TABLE_NAME
ORDER BY TABLE_NAME;

-- 2. Declared primary, unique, and foreign keys
-- Observed: four dimension primary keys, all ENABLED and VALIDATED.
-- No P/U/R constraint returned for MPHA_FACT_CLAIMS_MONTHLY.
-- Absence of a declared FK does not mean that an analytical join is absent.
SELECT
    C.TABLE_NAME || ' | ' || C.CONSTRAINT_TYPE || ' | ' ||
    LISTAGG(CC.COLUMN_NAME, ',') WITHIN GROUP (ORDER BY CC.POSITION) ||
    ' -> ' || NVL(MAX(P.TABLE_NAME), '-') || '(' ||
    LISTAGG(PC.COLUMN_NAME, ',') WITHIN GROUP (ORDER BY CC.POSITION) ||
    ') | ' || C.STATUS || ' | ' || C.VALIDATED AS RELATIONSHIP
FROM ALL_CONSTRAINTS C
JOIN ALL_CONS_COLUMNS CC
  ON CC.OWNER = C.OWNER AND CC.CONSTRAINT_NAME = C.CONSTRAINT_NAME
LEFT JOIN ALL_CONSTRAINTS P
  ON P.OWNER = C.R_OWNER AND P.CONSTRAINT_NAME = C.R_CONSTRAINT_NAME
LEFT JOIN ALL_CONS_COLUMNS PC
  ON PC.OWNER = P.OWNER
 AND PC.CONSTRAINT_NAME = P.CONSTRAINT_NAME
 AND PC.POSITION = CC.POSITION
WHERE C.OWNER = 'ORIGAMI_ADMIN02'
  AND C.TABLE_NAME IN (
      'MPHA_FACT_CLAIMS_MONTHLY', 'MPHA_DIM_DATE', 'MPHA_DIM_DISTRICT',
      'MPHA_DIM_COVERAGE_PROGRAM', 'MPHA_DIM_CLAIM_TYPE'
  )
  AND C.CONSTRAINT_TYPE IN ('P', 'U', 'R')
GROUP BY C.TABLE_NAME, C.CONSTRAINT_NAME, C.CONSTRAINT_TYPE,
         C.STATUS, C.VALIDATED
ORDER BY C.TABLE_NAME, C.CONSTRAINT_TYPE;

-- 3. Existing flattened view and actual join predicates
-- Expected joins from the inspected definition:
-- F.SERVICE_MONTH_DATE_KEY = D.DATE_KEY
-- F.DISTRICT_KEY = DIS.DISTRICT_KEY
-- F.PROGRAM_KEY = P.PROGRAM_KEY
-- F.CLAIM_TYPE_KEY = CT.CLAIM_TYPE_KEY
SELECT VIEW_NAME, TEXT_VC AS VIEW_DEFINITION
FROM ALL_VIEWS
WHERE OWNER = 'ORIGAMI_ADMIN02'
  AND VIEW_NAME = 'MPHA_OAC_STAR_CLAIMS';

-- 4. Fact grain, additive measures, and weighted ratio reconstruction
-- Observed result in column order:
-- 622 | 622 | 1400 | 1214 | 121 | 65 | 896370.39 | 8.6429 | 13.5894
-- PAID is in the source monetary unit; currency has not been established.
-- DATE_KEY/other key columns are NUMBER; ':' prevents concatenation ambiguity.
-- The join audit below found no missing dimension keys in this snapshot.
SELECT
    COUNT(*) AS FACT_ROWS,
    COUNT(DISTINCT SERVICE_MONTH_DATE_KEY || ':' || DISTRICT_KEY || ':' ||
                   PROGRAM_KEY || ':' || CLAIM_TYPE_KEY) AS DISTINCT_GRAIN,
    SUM(CLAIMS_SUBMITTED) AS SUBMITTED,
    SUM(APPROVED_CLAIMS) AS APPROVED,
    SUM(DENIED_CLAIMS) AS DENIED,
    SUM(PENDING_CLAIMS) AS PENDING,
    SUM(TOTAL_PAID_AMOUNT) AS PAID,
    ROUND(100 * SUM(DENIED_CLAIMS) /
          NULLIF(SUM(CLAIMS_SUBMITTED), 0), 4) AS DENIAL_PERCENT,
    ROUND(SUM(AVG_PROCESSING_DAYS * CLAIMS_SUBMITTED) /
          NULLIF(SUM(CLAIMS_SUBMITTED), 0), 4) AS WEIGHTED_DAYS_APPROX
FROM ORIGAMI_ADMIN02.MPHA_FACT_CLAIMS_MONTHLY;

-- 5. Join completeness, reporting period, and per-row status reconciliation
-- Observed result in column order:
-- 622 | 2025-01-01 | 2025-06-01 | 0 | 0 | 0
-- All four dimension PKs were validated; the joined row count remains 622.
-- A status equality check does not establish the business meaning of pending.
SELECT
    COUNT(*) AS JOINED_ROWS,
    TO_CHAR(MIN(D.FULL_DATE), 'YYYY-MM-DD') AS FIRST_MONTH,
    TO_CHAR(MAX(D.FULL_DATE), 'YYYY-MM-DD') AS LAST_MONTH,
    SUM(CASE WHEN D.DATE_KEY IS NULL OR X.DISTRICT_KEY IS NULL
                   OR P.PROGRAM_KEY IS NULL OR C.CLAIM_TYPE_KEY IS NULL
             THEN 1 ELSE 0 END) AS MISSING_DIMENSION_ROWS,
    SUM(CASE WHEN F.CLAIMS_SUBMITTED = F.APPROVED_CLAIMS + F.DENIED_CLAIMS
                                      + F.PENDING_CLAIMS
             THEN 0 ELSE 1 END) AS STATUS_MISMATCH_ROWS,
    SUM(CASE WHEN F.CLAIMS_SUBMITTED = 0 THEN 1 ELSE 0 END)
        AS ZERO_SUBMITTED_ROWS
FROM ORIGAMI_ADMIN02.MPHA_FACT_CLAIMS_MONTHLY F
LEFT JOIN ORIGAMI_ADMIN02.MPHA_DIM_DATE D
  ON F.SERVICE_MONTH_DATE_KEY = D.DATE_KEY
LEFT JOIN ORIGAMI_ADMIN02.MPHA_DIM_DISTRICT X
  ON F.DISTRICT_KEY = X.DISTRICT_KEY
LEFT JOIN ORIGAMI_ADMIN02.MPHA_DIM_COVERAGE_PROGRAM P
  ON F.PROGRAM_KEY = P.PROGRAM_KEY
LEFT JOIN ORIGAMI_ADMIN02.MPHA_DIM_CLAIM_TYPE C
  ON F.CLAIM_TYPE_KEY = C.CLAIM_TYPE_KEY;

-- Proposed semantic measure mapping:
-- Additive counts and amount columns: SUM.
-- Helper physical row expression: AVG_PROCESSING_DAYS * CLAIMS_SUBMITTED.
-- Aggregate that helper with SUM as Processing Days Total Approx.
-- Logical denial rate: aggregated Denied Claims / aggregated Claims Submitted.
-- Logical approximate days: aggregated helper / aggregated Claims Submitted.
-- Guard both denominators; keep rate as a ratio and apply Percent once.
-- Hide stored DENIAL_RATE and AVG_PROCESSING_DAYS from routine presentation.
-- Do not join the separate MPHA_FACT_DISTRICT_CLAIMS_CONTEXT into this starter
-- without validating its grain and defining an appropriate cross-fact model.
