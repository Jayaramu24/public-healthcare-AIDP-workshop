# Public Healthcare AIDP Workshop
# Claims star schema notebook: Silver Delta tables -> connected Autonomous AI Lakehouse external catalog tables.
#
# Purpose:
# - Build the instructor-led Claims star schema directly inside AIDP
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


silver_base = "oci://<bucket>@<namespace>/mpha/silver"
target_catalog = "MPHA_AILH_CAT"
target_schema = "MPHA_GOLD_OWNER"
table_prefix = "mpha"
write_mode = "append"


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


silver_district = read_delta("silver_district")
silver_claims_membership_disbursement = read_delta("silver_claims_membership_disbursement")


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

claims_with_service_month = silver_claims_membership_disbursement.withColumn(
    "service_month",
    F.to_date(F.date_format(F.col("service_date"), "yyyy-MM-01")),
)


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
