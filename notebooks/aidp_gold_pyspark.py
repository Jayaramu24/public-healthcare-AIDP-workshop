# Public Healthcare AIDP Workshop
# Gold notebook: Silver Delta tables -> Gold-serving stage files for AI Lakehouse and OAC.
#
# Run `aidp_silver_pyspark.py` first so the Silver tables exist.

from pyspark.sql import functions as F
from pyspark.sql.window import Window


silver_base = "oci://<bucket>@<namespace>/mpha/silver"
gold_stage_base = "oci://<bucket>@<namespace>/mpha/gold_stage"
gold_snapshot_date = F.to_date(F.lit("2025-06-30"))


def read_delta(name):
    return spark.read.format("delta").load(f"{silver_base}/{name}")


def write_stage_csv(frame, name):
    frame.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{gold_stage_base}/{name}")


silver_district = read_delta("silver_district")
silver_facility_provider = read_delta("silver_facility_provider")
silver_facility_day = read_delta("silver_facility_day")
silver_population_health_week = read_delta("silver_population_health_week")
silver_district_health_week = read_delta("silver_district_health_week")
silver_claims_membership_disbursement = read_delta("silver_claims_membership_disbursement")
silver_provider_accreditation = read_delta("silver_provider_accreditation")
silver_facility_capacity_event = read_delta("silver_facility_capacity_event")
silver_spatial_feature = read_delta("silver_spatial_feature")


gold_facility_access_daily = (
    silver_facility_day.alias("f")
    .join(
        silver_facility_provider.select("facility_id", "facility_name", "district_name", "provider_id", "provider_name").alias("p"),
        "facility_id",
        "left",
    )
)

# `silver_district_health_week` already carries district attributes from the
# Silver-layer conformance join, so keep it as-is and avoid reintroducing
# duplicate columns such as `district_name`.
gold_district_public_health_weekly = silver_district_health_week

gold_immunization_equity_weekly = silver_population_health_week.join(
    silver_district.select("district_id", "district_name", "deprivation_index", "elderly_pct"),
    "district_id",
    "left",
)

gold_claims_summary = (
    silver_claims_membership_disbursement.withColumn(
        "service_month",
        F.to_date(F.date_format(F.col("service_date"), "yyyy-MM-01")),
    )
    .groupBy("service_month", "district_id", "program_code", "coverage_program", "claim_type", "service_category", "diagnosis_group")
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
)

gold_disbursement_summary = (
    silver_claims_membership_disbursement.withColumn(
        "disbursement_month",
        F.to_date(F.date_format(F.coalesce(F.col("disbursement_date"), F.col("service_date")), "yyyy-MM-01")),
    )
    .groupBy("disbursement_month", "district_id", "program_code", "coverage_program", "payee_type")
    .agg(
        F.countDistinct("disbursement_id").alias("disbursement_records"),
        F.sum(F.when(F.col("payment_status") == "Paid", 1).otherwise(0)).alias("paid_records"),
        F.sum(F.when(F.col("payment_status") == "Pending", 1).otherwise(0)).alias("pending_records"),
        F.sum(F.when(F.col("payment_status") == "Failed", 1).otherwise(0)).alias("failed_records"),
        F.round(F.sum("disbursement_amount"), 2).alias("total_disbursement_amount"),
        F.round(F.avg("payment_cycle_days"), 1).alias("avg_payment_cycle_days"),
    )
)

membership_snapshot = silver_claims_membership_disbursement.select(
    "member_id",
    "district_id",
    "program_code",
    "coverage_program",
    "age_group",
    "risk_segment",
    "chronic_condition_flag",
    "eligibility_status",
    "renewal_due_date",
)

gold_membership_summary = (
    membership_snapshot.withColumn("snapshot_month", F.lit("2025-06-01").cast("date"))
    .groupBy("snapshot_month", "district_id", "program_code", "coverage_program", "age_group", "risk_segment", "chronic_condition_flag")
    .agg(
        F.countDistinct("member_id").alias("members"),
        F.countDistinct(F.when(F.col("eligibility_status") == "Active", F.col("member_id"))).alias("active_members"),
        F.countDistinct(
            F.when(
                F.datediff(F.col("renewal_due_date"), F.col("snapshot_month")).between(0, 60),
                F.col("member_id"),
            )
        ).alias("renewal_due_within_60_days"),
        F.countDistinct(
            F.when(
                (F.col("risk_segment").isin("High", "Rising")) | (F.col("chronic_condition_flag") == "Y"),
                F.col("member_id"),
            )
        ).alias("high_risk_members"),
        F.countDistinct(F.when(F.col("eligibility_status") != "Active", F.col("member_id"))).alias("inactive_or_suspended_members"),
    )
)

gold_provider_accreditation_summary = (
    silver_provider_accreditation.withColumn("snapshot_date", gold_snapshot_date)
    .select(
        "snapshot_date",
        "district_id",
        "district_name",
        "facility_id",
        "facility_name",
        "provider_id",
        "provider_name",
        "accreditation_body",
        "accreditation_status",
        "accreditation_level",
        "accreditation_score",
        "corrective_action_count",
        "days_to_expiry",
        "accreditation_pressure_band",
        "specialty_scope",
    )
)

latest_capacity_window = Window.partitionBy("facility_id").orderBy(F.col("event_timestamp").desc())
gold_capacity_event_latest = (
    silver_facility_capacity_event.withColumn("facility_event_rank", F.row_number().over(latest_capacity_window))
    .filter(F.col("facility_event_rank") == 1)
    .drop("facility_event_rank")
)

latest_district_window = Window.partitionBy("district_id").orderBy(F.col("week_start_date").desc())
latest_district_pressure = (
    silver_district_health_week.withColumn("district_week_rank", F.row_number().over(latest_district_window))
    .filter(F.col("district_week_rank") == 1)
    .drop("district_week_rank")
)

district_facility_footprint = (
    silver_facility_provider.groupBy("district_id")
    .agg(
        F.countDistinct("facility_id").alias("facility_count"),
        F.countDistinct("provider_id").alias("provider_count"),
    )
)

district_catchments = (
    silver_spatial_feature.filter(F.col("source_layer") == "facility_catchment")
    .groupBy("district_id")
    .agg(F.countDistinct("facility_id").alias("catchment_count"))
)

gold_spatial_access_insights = (
    latest_district_pressure.join(district_facility_footprint, "district_id", "left")
    .join(district_catchments, "district_id", "left")
    .withColumn("facility_count", F.coalesce(F.col("facility_count"), F.lit(1)))
    .withColumn("catchment_count", F.coalesce(F.col("catchment_count"), F.col("facility_count")))
    .withColumn("residents_per_facility", F.round(F.col("population") / F.col("facility_count"), 0))
    .withColumn(
        "avg_travel_distance_km",
        F.round(
            F.greatest(
                F.lit(0.8),
                F.col("deprivation_index") * F.lit(1.8) + F.col("residents_per_facility") / F.lit(75000.0),
            ),
            2,
        ),
    )
    .withColumn(
        "recommended_action",
        F.when(
            (F.col("public_health_pressure_index") >= 45) | (F.col("residents_per_facility") >= 30000),
            F.lit("Prioritize mobile clinic sessions and outreach routing"),
        )
        .when(
            (F.col("public_health_pressure_index") >= 35) | (F.col("avg_travel_distance_km") >= 1.5),
            F.lit("Review catchment coverage and extend community clinic hours"),
        )
        .otherwise(F.lit("Maintain standard catchment monitoring")),
    )
    .select(
        "district_id",
        "district_name",
        "public_health_pressure_index",
        "facility_count",
        "provider_count",
        "catchment_count",
        "residents_per_facility",
        "avg_travel_distance_km",
        "recommended_action",
    )
)

gold_executive_overview = (
    silver_facility_day.agg(
        F.lit("2025 H1").alias("reporting_period"),
        (F.sum("outpatient_visits") + F.sum("emergency_arrivals")).alias("total_visits"),
        F.round(F.avg("avg_ed_wait_minutes"), 1).alias("avg_ed_wait_minutes"),
        F.sum(F.when(F.col("high_occupancy_flag") == "Y", 1).otherwise(0)).alias("high_occupancy_days"),
        F.round(F.avg("access_risk_score"), 1).alias("avg_access_risk_score"),
    )
)

gold_tables = {
    "gold_facility_access_daily": gold_facility_access_daily,
    "gold_district_public_health_weekly": gold_district_public_health_weekly,
    "gold_immunization_equity_weekly": gold_immunization_equity_weekly,
    "gold_claims_summary": gold_claims_summary,
    "gold_disbursement_summary": gold_disbursement_summary,
    "gold_membership_summary": gold_membership_summary,
    "gold_provider_accreditation_summary": gold_provider_accreditation_summary,
    "gold_capacity_event_latest": gold_capacity_event_latest,
    "gold_spatial_access_insights": gold_spatial_access_insights,
    "gold_executive_overview": gold_executive_overview,
}


for table_name, frame in gold_tables.items():
    write_stage_csv(frame, table_name)
    print(f"Staged {table_name} under {gold_stage_base}/{table_name}")


print(
    "Gold staging complete. Load the dimensional AI Lakehouse model with sql/create_ai_lakehouse_dimensional_gold_schema.sql."
)
