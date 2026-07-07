# Public Healthcare AIDP Workshop
# Round 2 extension notebook: Silver operations/access context -> Gold district Claims context -> AI Lakehouse.
#
# Purpose:
# - Extend the existing Claims analytics product without rebuilding the Claims star schema
# - Aggregate JSON capacity and spatial access context to district-month grain
# - Write the context table to the connected Autonomous AI Lakehouse external catalog
#
# Run after:
# - 02_Silver_Public_Healthcare.ipynb
# - aidp_claims_context_silver_pyspark.py
# - sql/create_ai_lakehouse_claims_context_extension.sql
#
# Output:
# - Delta/staged Gold: gold_district_claims_context
# - AI Lakehouse table: mpha_fact_district_claims_context

from pyspark.sql import functions as F


silver_base = "/Volumes/e2eindustrydemos/default/e2eindustrydemovol/Silver"
gold_stage_base = "/Volumes/e2eindustrydemos/default/e2eindustrydemovol/gold_stage"

# Update these three values if your external catalog, schema, or table prefix differ.
target_catalog = "goldailh"
target_schema = "e2eaidpuser"
table_prefix = "mpha"
write_to_ai_lakehouse = True
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
            "Update target_catalog and target_schema to the connected AI Lakehouse external catalog."
        )


def validate_target_tables(required_tables):
    available = {
        row.tableName
        for row in spark.sql(f"SHOW TABLES IN {target_catalog}.{target_schema}").collect()
    }
    missing = [table for table in required_tables if f"{table_prefix}_{table}" not in available]
    if missing:
        raise ValueError(
            "These required AI Lakehouse extension tables are missing: "
            + ", ".join(f"{table_prefix}_{name}" for name in missing)
            + ". Run sql/create_ai_lakehouse_claims_context_extension.sql first."
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


silver_operations_access_context = read_delta("silver_operations_access_context")
silver_claims_membership_disbursement = read_delta("silver_claims_membership_disbursement")


operations_monthly = (
    silver_operations_access_context.withColumn(
        "context_month",
        F.to_date(F.date_format(F.col("event_date"), "yyyy-MM-01")),
    )
    .groupBy("context_month", "district_id", "district_name")
    .agg(
        F.countDistinct("event_id").alias("capacity_event_count"),
        F.round(F.avg("current_occupancy_rate"), 4).alias("avg_occupancy_rate"),
        F.round(F.max("current_occupancy_rate"), 4).alias("max_occupancy_rate"),
        F.round(F.avg("waiting_room_count"), 1).alias("avg_waiting_room_count"),
        F.round(F.avg("avg_ed_wait_minutes"), 1).alias("avg_ed_wait_minutes"),
        F.sum(F.when(F.col("capacity_pressure_band") == "High", 1).otherwise(0)).alias("high_capacity_event_count"),
        F.sum(F.when(F.col("diversion_event_flag") == "Y", 1).otherwise(0)).alias("diversion_event_count"),
        F.sum(F.when(F.col("supply_alert_count") > 0, 1).otherwise(0)).alias("supply_alert_event_count"),
        F.round(F.avg("triage_acuity_score"), 1).alias("avg_triage_acuity_score"),
        F.max("facility_count").alias("facility_count"),
        F.max("catchment_count").alias("catchment_count"),
        F.max("residents_per_facility").alias("residents_per_facility"),
        F.max("access_gap_score").alias("access_gap_score"),
        F.max("operations_access_risk_score").alias("operations_access_risk_score"),
    )
)


claims_monthly = (
    silver_claims_membership_disbursement.withColumn(
        "context_month",
        F.to_date(F.date_format(F.col("service_date"), "yyyy-MM-01")),
    )
    .groupBy("context_month", "district_id")
    .agg(
        F.count("*").alias("claims_submitted"),
        F.sum(F.when(F.col("claim_status") == "Denied", 1).otherwise(0)).alias("denied_claims"),
        F.round(F.avg("processing_days"), 1).alias("avg_processing_days"),
        F.round(F.sum("submitted_amount"), 2).alias("total_submitted_amount"),
        F.round(F.sum("paid_amount"), 2).alias("total_paid_amount"),
    )
    .withColumn(
        "denial_rate",
        F.round(F.col("denied_claims") / F.greatest(F.col("claims_submitted"), F.lit(1)), 4),
    )
)


gold_district_claims_context = (
    operations_monthly.join(claims_monthly, ["context_month", "district_id"], "left")
    .withColumn("claims_submitted", F.coalesce(F.col("claims_submitted"), F.lit(0)))
    .withColumn("denied_claims", F.coalesce(F.col("denied_claims"), F.lit(0)))
    .withColumn("avg_processing_days", F.coalesce(F.col("avg_processing_days"), F.lit(0.0)))
    .withColumn("total_submitted_amount", F.coalesce(F.col("total_submitted_amount"), F.lit(0.0)))
    .withColumn("total_paid_amount", F.coalesce(F.col("total_paid_amount"), F.lit(0.0)))
    .withColumn("denial_rate", F.coalesce(F.col("denial_rate"), F.lit(0.0)))
    .withColumn(
        "claims_context_priority_score",
        F.round(
            F.least(
                F.lit(100.0),
                F.col("denial_rate") * F.lit(100.0) * F.lit(0.35)
                + F.col("avg_processing_days") * F.lit(0.75)
                + F.col("high_capacity_event_count") * F.lit(3.0)
                + F.col("diversion_event_count") * F.lit(5.0)
                + F.col("access_gap_score") * F.lit(0.25),
            ),
            1,
        ),
    )
    .withColumn(
        "recommended_action",
        F.when(
            (F.col("claims_context_priority_score") >= 70)
            & (F.col("access_gap_score") >= 45)
            & (F.col("high_capacity_event_count") >= 2),
            F.lit("Prioritize claims review, provider outreach, and mobile clinic scheduling"),
        )
        .when(
            (F.col("denial_rate") >= 0.18) & (F.col("avg_processing_days") >= 18),
            F.lit("Prioritize claims denial review and processing backlog reduction"),
        )
        .when(
            (F.col("access_gap_score") >= 45) | (F.col("diversion_event_count") >= 1),
            F.lit("Review access coverage and route community services"),
        )
        .otherwise(F.lit("Monitor through standard claims operations cadence")),
    )
    .select(
        "context_month",
        "district_id",
        "district_name",
        "claims_submitted",
        "denied_claims",
        "denial_rate",
        "avg_processing_days",
        "total_submitted_amount",
        "total_paid_amount",
        "capacity_event_count",
        "avg_occupancy_rate",
        "max_occupancy_rate",
        "avg_waiting_room_count",
        "avg_ed_wait_minutes",
        "high_capacity_event_count",
        "diversion_event_count",
        "supply_alert_event_count",
        "avg_triage_acuity_score",
        "facility_count",
        "catchment_count",
        "residents_per_facility",
        "access_gap_score",
        "operations_access_risk_score",
        "claims_context_priority_score",
        "recommended_action",
    )
)


gold_district_claims_context.write.format("delta").mode("overwrite").save(f"{gold_stage_base}/gold_district_claims_context")
print(f"Wrote Gold context Delta output to {gold_stage_base}/gold_district_claims_context")


if write_to_ai_lakehouse:
    validate_target_namespace()
    validate_target_tables(["fact_district_claims_context", "dim_date", "dim_district"])

    dim_date_lookup = spark.table(target_table("dim_date")).select(
        F.col("date_key").alias("context_month_date_key"),
        F.col("full_date").alias("context_month"),
    )
    dim_district_lookup = spark.table(target_table("dim_district")).select("district_key", "district_id")

    fact_district_claims_context = (
        gold_district_claims_context.join(dim_date_lookup, "context_month", "left")
        .join(dim_district_lookup, "district_id", "left")
        .select(
            "context_month_date_key",
            "district_key",
            "claims_submitted",
            "denied_claims",
            "denial_rate",
            "avg_processing_days",
            "total_submitted_amount",
            "total_paid_amount",
            "capacity_event_count",
            "avg_occupancy_rate",
            "max_occupancy_rate",
            "avg_waiting_room_count",
            "avg_ed_wait_minutes",
            "high_capacity_event_count",
            "diversion_event_count",
            "supply_alert_event_count",
            "avg_triage_acuity_score",
            "facility_count",
            "catchment_count",
            "residents_per_facility",
            "access_gap_score",
            "operations_access_risk_score",
            "claims_context_priority_score",
            "recommended_action",
        )
    )

    if fact_district_claims_context.filter(F.col("context_month_date_key").isNull() | F.col("district_key").isNull()).count() > 0:
        raise ValueError(
            "Some context rows could not map to AI Lakehouse dim_date or dim_district. "
            "Confirm the Claims star schema dimensions were loaded before this extension."
        )

    write_catalog_table(
        fact_district_claims_context,
        "fact_district_claims_context",
        [
            "context_month_date_key",
            "district_key",
            "claims_submitted",
            "denied_claims",
            "denial_rate",
            "avg_processing_days",
            "total_submitted_amount",
            "total_paid_amount",
            "capacity_event_count",
            "avg_occupancy_rate",
            "max_occupancy_rate",
            "avg_waiting_room_count",
            "avg_ed_wait_minutes",
            "high_capacity_event_count",
            "diversion_event_count",
            "supply_alert_event_count",
            "avg_triage_acuity_score",
            "facility_count",
            "catchment_count",
            "residents_per_facility",
            "access_gap_score",
            "operations_access_risk_score",
            "claims_context_priority_score",
            "recommended_action",
        ],
        ["context_month_date_key", "district_key"],
    )


print("Round 2 Gold context complete.")
gold_district_claims_context.orderBy(F.desc("claims_context_priority_score")).show(25, truncate=False)
