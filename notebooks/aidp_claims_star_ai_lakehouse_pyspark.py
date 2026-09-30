# %% [markdown]
# # Before you run: your assigned environment
#
# Use your preloaded notebook when available. If restoring this common download,
# copy the exact administrator-assigned values into its setup cell:
# `participant_id`, `volume_base` (shared raw input) and `output_base` (your own
# output volume). In the Lakehouse notebooks and notebook 99 also set
# `target_catalog` and `target_schema`. Do not infer paths from your name or copy
# another participant's values from a screenshot. The administrator must enforce
# access permissions; string validation is not a security boundary.
#
# Notebook filenames do not change when lab numbers change. Run 01, 02, 03 and 04
# in order. Then follow the guide for 02B/03B, 05, the workflow and agents.
# Notebook 99 contains on-demand read-only inspection examples.
#
# Bronze/Silver/Gold overwrite only the assigned output snapshot. Lakehouse loads
# append missing keys and are safe to repeat with unchanged source/reference data;
# they do not update existing measures or implement general CDC. Do not change
# dimension members or source snapshots without a reviewed loading strategy.
#
# This common download changes configuration only, not the tested transformation
# logic. A restore into a different tenancy still requires its readiness and
# execution checks. Use Python as notebook default; select SQL only for SQL cells.

# %% [markdown]
# # 04 Claims Star Schema - Publish Gold to AI Lakehouse
#
# ## What this section does and why it matters
# Builds Date, District, Coverage Program, Claim Type dimensions and the monthly Claims fact, then inserts only new rows into the connected AI Lakehouse external catalog.
#
# **Why it matters:** This is the governed business data product used by OAC, OAC Assistant, ML features, and the Claims SQL Agent.
#
# ## Inputs and outputs
#
# **Inputs**
# - Participant Silver Delta folders under `<output_base>/silver`
# - Pre-created Claims star schema tables in the assigned AI Lakehouse schema, such as `goldailh.MPHA_P17`
# - AIDP external catalog refresh completed so the participant schema is visible under `goldailh`
#
# **Outputs**
# - mpha_dim_date
# - mpha_dim_district
# - mpha_dim_coverage_program
# - mpha_dim_claim_type
# - mpha_fact_claims_monthly
#
# ## Important parameters participants may change
# - `volume_base`
# - `participant_id`
# - `silver_base`
# - `target_catalog`
# - `target_schema`
# - `table_prefix`
# - `write_mode`

# %% [markdown]
# ## Plain-language explanation before the code
# Run the code cells from top to bottom. The early cells configure paths and helpers, the middle cells build or transform the data, and the final cells write outputs and display validation evidence.
#
# Keep the parameter values aligned with the Object Storage bucket, AIDP volume, external catalog, and schema prepared in Lab 0. If you change an input path, rerun the upstream notebook before rerunning this one.

# %% [markdown]
# ## Code section - Imports and setup
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# Public Healthcare AIDP Workshop
# Claims star schema notebook: Silver Delta tables -> connected Autonomous AI Lakehouse external catalog tables.
#
# Purpose:
# - Build the guided Claims star schema directly inside AIDP
# - Write the star schema tables to the connected external AI Lakehouse catalog
# - Keep participants inside the AIDP notebook flow instead of switching to manual SQL loading
#
# Assumptions:
# 1. The external AI Lakehouse catalog is already connected in AIDP.
# 2. The target schema already contains these tables:
#    - mpha_dim_date
#    - mpha_dim_district
#    - mpha_dim_coverage_program
#    - mpha_dim_claim_type
#    - mpha_fact_claims_monthly
# 3. The target user/schema has sufficient quota on tablespace DATA for inserts.
# 4. Run `aidp_silver_pyspark.py` first so the Silver Delta tables exist.

from pyspark.sql import functions as F
from pyspark.sql.window import Window


# %% [markdown]
# ## Code section - Configure source and target catalog values
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 1. Configure source and target catalog values.
# All participants read their own Silver output from workshop_runs/<participant_id>.
# Each participant writes to their assigned AI Lakehouse schema, for example
# MPHA_P01 through MPHA_P17. The validated smoke test used MPHA_P17.
# -----------------------------------------------------------------------------
volume_base = "REPLACE_WITH_SHARED_RAW_VOLUME"
# Copy the exact mounted paths from the administrator's configuration sheet.
# Shared input and personal outputs must be separate; never write into raw.
output_base = "REPLACE_WITH_YOUR_OUTPUT_VOLUME"
if "REPLACE_" in volume_base or "REPLACE_" in output_base:
    raise ValueError("Set volume_base and output_base from your assigned configuration.")
if not volume_base.startswith("/Volumes/") or not output_base.startswith("/Volumes/"):
    raise ValueError("Use the exact /Volumes/ mounts supplied by the administrator.")
volume_base = volume_base.rstrip("/")
output_base = output_base.rstrip("/")
if output_base == volume_base or output_base.startswith(volume_base + "/"):
    raise ValueError("Output must be your separate personal volume, not shared raw.")
print("Input volume:", volume_base, "Personal outputs:", output_base)

participant_id = "REPLACE_WITH_YOUR_PARTICIPANT_ID"  # Exact assigned folder name.

if participant_id == "REPLACE_WITH_YOUR_PARTICIPANT_ID":
    raise ValueError("Set participant_id to your AIDP participant folder name before running this notebook.")

silver_base = f"{output_base}/silver"
target_catalog = "REPLACE_WITH_YOUR_AILH_CATALOG"
target_schema = "REPLACE_WITH_YOUR_AILH_SCHEMA"  # Assigned schema; not a screenshot example.

if target_schema == "REPLACE_WITH_YOUR_AILH_SCHEMA":
    raise ValueError("Set target_schema to your assigned AI Lakehouse schema, from your configuration sheet.")

table_prefix = "mpha"
write_mode = "append"

if "REPLACE_" in target_catalog or "REPLACE_" in target_schema:
    raise ValueError("Set your assigned external catalog and schema before continuing.")


# %% [markdown]
# ## Code section - Shared helpers
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 2. Shared helpers.
# `write_catalog_table` appends only rows that do not already exist by the
# natural key, making reruns safer for workshop participants.
# -----------------------------------------------------------------------------
def read_delta(name):
    return spark.read.format("delta").load(f"{silver_base}/{name}")


def target_table(name):
    return f"{target_catalog}.{target_schema}.{table_prefix}_{name}"


def validate_target_namespace():
    schema_rows = spark.sql(f"SHOW SCHEMAS IN {target_catalog} LIKE '{target_schema}'").collect()
    if not schema_rows:
        raise ValueError(
            f"Target schema {target_catalog}.{target_schema} was not found. "
            "Update `target_catalog` / `target_schema` to an existing external AI Lakehouse catalog schema, "
            "or create the schema and base tables first."
        )


def validate_target_tables(required_tables):
    available = {
        row.tableName
        for row in spark.sql(f"SHOW TABLES IN {target_catalog}.{target_schema}").collect()
    }
    missing = [table for table in required_tables if f"{table_prefix}_{table}" not in available]
    if missing:
        raise ValueError(
            "The target schema exists, but these required star-schema tables are missing: "
            + ", ".join(f"{table_prefix}_{name}" for name in missing)
            + ". Create them first in Autonomous AI Lakehouse before running this notebook."
        )


def write_catalog_table(frame, name, columns, key_columns):
    table_name = target_table(name)
    ordered = frame.select(*columns)
    existing_keys = spark.table(table_name).select(*key_columns).dropDuplicates()
    new_rows = ordered.join(existing_keys, key_columns, "left_anti")
    new_row_count = new_rows.count()
    if new_row_count == 0:
        print(f"No new rows to write for {table_name}")
        return
    new_rows.write.mode(write_mode).insertInto(table_name)
    print(f"Wrote {new_row_count} new rows to {table_name}")


# %% [markdown]
# ## Code section - Load the Silver sources used for the Claims star schema
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 3. Load the Silver sources used for the Claims star schema.
# District is used as a dimension; the claims-membership-disbursement table is
# the transactional source for date, program, claim-type, and fact tables.
# -----------------------------------------------------------------------------
silver_district = read_delta("silver_district")
silver_claims_membership_disbursement = read_delta("silver_claims_membership_disbursement")


# %% [markdown]
# ## Code section - Validate the external AI Lakehouse schema before doing any writes
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 4. Validate the external AI Lakehouse schema before doing any writes.
# Failing early gives a clear error if the schema or required tables were not
# created in Autonomous AI Lakehouse.
# -----------------------------------------------------------------------------
validate_target_namespace()
validate_target_tables(
    [
        "dim_date",
        "dim_district",
        "dim_coverage_program",
        "dim_claim_type",
        "fact_claims_monthly",
    ]
)


# %% [markdown]
# ## Code section - Add service-month grain to the claims source
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 5. Add service-month grain to the claims source.
# The final fact table is monthly by district, coverage program, and claim type.
# -----------------------------------------------------------------------------
claims_with_service_month = silver_claims_membership_disbursement.withColumn(
    "service_month",
    F.to_date(F.date_format(F.col("service_date"), "yyyy-MM-01")),
)


# %% [markdown]
# ## Code section - Build the Date dimension from all claim lifecycle dates
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 6. Build the Date dimension from all claim lifecycle dates.
# Including enrollment, renewal, service, receipt, and disbursement dates makes
# the date dimension useful for future dashboard extensions.
# -----------------------------------------------------------------------------
date_values = (
    silver_claims_membership_disbursement.select(F.col("service_date").alias("full_date"))
    .union(silver_claims_membership_disbursement.select(F.col("claim_received_date").alias("full_date")))
    .union(silver_claims_membership_disbursement.select(F.col("disbursement_date").alias("full_date")))
    .union(silver_claims_membership_disbursement.select(F.col("enrollment_date").alias("full_date")))
    .union(silver_claims_membership_disbursement.select(F.col("renewal_due_date").alias("full_date")))
    .union(claims_with_service_month.select(F.col("service_month").alias("full_date")))
    .filter(F.col("full_date").isNotNull())
    .distinct()
)


# %% [markdown]
# ## Code section - Build dimension tables
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 7. Build dimension tables.
# Surrogate keys are generated deterministically from sorted business keys so
# fact rows can resolve to compact integer keys in AI Lakehouse.
# -----------------------------------------------------------------------------
dim_date = (
    date_values.withColumn("date_key", F.date_format("full_date", "yyyyMMdd").cast("int"))
    .withColumn("calendar_year", F.year("full_date"))
    .withColumn("calendar_quarter", F.quarter("full_date"))
    .withColumn("month_number", F.month("full_date"))
    .withColumn("month_name", F.date_format("full_date", "MMMM"))
    .withColumn("week_start_date", F.date_sub(F.next_day(F.col("full_date"), "Mon"), 7))
    .withColumn("day_of_week", F.date_format("full_date", "EEEE"))
    .withColumn("is_week_start", F.when(F.dayofweek("full_date") == 2, F.lit("Y")).otherwise(F.lit("N")))
    .select(
        "date_key",
        "full_date",
        "calendar_year",
        "calendar_quarter",
        "month_number",
        "month_name",
        "week_start_date",
        "day_of_week",
        "is_week_start",
    )
)


dim_district = (
    silver_district.orderBy("district_id")
    .withColumn("district_key", F.row_number().over(Window.orderBy("district_id")))
    .select(
        "district_key",
        "district_id",
        "district_name",
        "population",
        "deprivation_index",
        "elderly_pct",
        "chronic_condition_pct",
        "median_income_usd",
    )
)


dim_coverage_program = (
    silver_claims_membership_disbursement.select(
        "program_code",
        "coverage_program",
        "program_type",
        "funding_source",
    )
    .dropDuplicates()
    .orderBy("program_code", "coverage_program", "program_type", "funding_source")
    .withColumn(
        "program_key",
        F.row_number().over(Window.orderBy("program_code", "coverage_program", "program_type", "funding_source")),
    )
    .select(
        "program_key",
        "program_code",
        "coverage_program",
        "program_type",
        "funding_source",
    )
)


dim_claim_type = (
    silver_claims_membership_disbursement.select(
        "claim_type",
        "service_category",
        "diagnosis_group",
    )
    .dropDuplicates()
    .orderBy("claim_type", "service_category", "diagnosis_group")
    .withColumn(
        "claim_type_key",
        F.row_number().over(Window.orderBy("claim_type", "service_category", "diagnosis_group")),
    )
    .select(
        "claim_type_key",
        "claim_type",
        "service_category",
        "diagnosis_group",
    )
)


# %% [markdown]
# ## Code section - Prepare lookup tables for fact-key resolution
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 8. Prepare lookup tables for fact-key resolution.
# These are not written directly; they map business columns to dimension keys.
# -----------------------------------------------------------------------------
district_lookup = dim_district.select("district_id", "district_key")
program_lookup = dim_coverage_program.select(
    "program_code",
    "coverage_program",
    "program_type",
    "funding_source",
    "program_key",
)
claim_type_lookup = dim_claim_type.select(
    "claim_type",
    "service_category",
    "diagnosis_group",
    "claim_type_key",
)


# %% [markdown]
# ## Code section - Build the monthly Claims fact table
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 9. Build the monthly Claims fact table.
# The fact table carries the dashboard measures: submitted, approved, denied,
# pending claims, submitted/approved/paid amount, processing days, and denial rate.
# -----------------------------------------------------------------------------
fact_claims_monthly = (
    claims_with_service_month.groupBy(
        "service_month",
        "district_id",
        "program_code",
        "coverage_program",
        "program_type",
        "funding_source",
        "claim_type",
        "service_category",
        "diagnosis_group",
    )
    .agg(
        F.count("*").alias("claims_submitted"),
        F.sum(F.when(F.col("claim_status") == "Approved", 1).otherwise(0)).alias("approved_claims"),
        F.sum(F.when(F.col("claim_status") == "Denied", 1).otherwise(0)).alias("denied_claims"),
        F.sum(F.when(F.col("claim_status") == "Pending", 1).otherwise(0)).alias("pending_claims"),
        F.round(F.sum("submitted_amount"), 2).alias("total_submitted_amount"),
        F.round(F.sum("approved_amount"), 2).alias("total_approved_amount"),
        F.round(F.sum("paid_amount"), 2).alias("total_paid_amount"),
        F.round(F.avg("processing_days"), 1).alias("avg_processing_days"),
    )
    .withColumn(
        "denial_rate",
        F.round(F.col("denied_claims") / F.greatest(F.col("claims_submitted"), F.lit(1)), 4),
    )
    .withColumn("service_month_date_key", F.date_format("service_month", "yyyyMMdd").cast("int"))
    .join(district_lookup, "district_id", "left")
    .join(
        program_lookup,
        ["program_code", "coverage_program", "program_type", "funding_source"],
        "left",
    )
    .join(
        claim_type_lookup,
        ["claim_type", "service_category", "diagnosis_group"],
        "left",
    )
    .select(
        "service_month_date_key",
        "district_key",
        "program_key",
        "claim_type_key",
        "claims_submitted",
        "approved_claims",
        "denied_claims",
        "pending_claims",
        "total_submitted_amount",
        "total_approved_amount",
        "total_paid_amount",
        "avg_processing_days",
        "denial_rate",
    )
)


# %% [markdown]
# ## Code section - Write dimensions first, then the fact table
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 10. Write dimensions first, then the fact table.
# This order keeps referential intent clear for participants inspecting the
# external catalog in AIDP or AI Lakehouse.
# -----------------------------------------------------------------------------
write_catalog_table(
    dim_date,
    "dim_date",
    [
        "date_key",
        "full_date",
        "calendar_year",
        "calendar_quarter",
        "month_number",
        "month_name",
        "week_start_date",
        "day_of_week",
        "is_week_start",
    ],
    ["date_key"],
)

write_catalog_table(
    dim_district,
    "dim_district",
    [
        "district_key",
        "district_id",
        "district_name",
        "population",
        "deprivation_index",
        "elderly_pct",
        "chronic_condition_pct",
        "median_income_usd",
    ],
    ["district_key"],
)

write_catalog_table(
    dim_coverage_program,
    "dim_coverage_program",
    [
        "program_key",
        "program_code",
        "coverage_program",
        "program_type",
        "funding_source",
    ],
    ["program_key"],
)

write_catalog_table(
    dim_claim_type,
    "dim_claim_type",
    [
        "claim_type_key",
        "claim_type",
        "service_category",
        "diagnosis_group",
    ],
    ["claim_type_key"],
)

write_catalog_table(
    fact_claims_monthly,
    "fact_claims_monthly",
    [
        "service_month_date_key",
        "district_key",
        "program_key",
        "claim_type_key",
        "claims_submitted",
        "approved_claims",
        "denied_claims",
        "pending_claims",
        "total_submitted_amount",
        "total_approved_amount",
        "total_paid_amount",
        "avg_processing_days",
        "denial_rate",
    ],
    ["service_month_date_key", "district_key", "program_key", "claim_type_key"],
)


print("Claims star schema write complete in the connected Autonomous AI Lakehouse catalog.")


# %% [markdown]
# ## Expected row counts or displayed results
# - mpha_fact_claims_monthly: about 622 rows on first successful load
# - dimension row counts should be non-zero, and the validation SQL should return zero orphan rows
#
# ## Safe rerun behaviour
# Designed for safe reruns. Existing natural keys are read from target tables and only new keys are inserted.
#
# ## Common errors and troubleshooting
# - Target schema not found: refresh the `goldailh` external catalog in AIDP and confirm the assigned schema, for example `MPHA_P17`, is visible.
# - Required table missing: run the Claims star schema DDL before this notebook.
# - Executor memory failure: use the validated 1G driver/executor memory setting from the workshop troubleshooting notes.
# - Table does not support truncate: do not truncate from Spark; use the idempotent append pattern.

# %% [markdown]
# ## What you learned
# You learned how AIDP can publish a governed Claims star schema directly into AI Lakehouse while remaining safe for repeat execution.
