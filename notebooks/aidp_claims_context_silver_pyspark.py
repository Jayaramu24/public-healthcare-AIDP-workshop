# PARTICIPANT NOTEBOOK GUIDE
# 02B Silver Extension - Add JSON and Spatial Context
#
# What this section does and why it matters:
# - Parses JSON facility capacity events, flattens GeoJSON service-area features, joins reference data, and creates a Silver operations/access context table.
# - Why it matters: This shows progressive enhancement: MPHA can add new operational signals after the original Claims dashboard is live without rebuilding the original Claims star schema.
#
# Inputs and outputs:
# - Inputs:
# - bronze_facility_capacity_events
# - bronze_healthcare_service_areas_geojson
# - bronze_facility_provider_master
# - bronze_district_health_profile
# - Outputs:
# - silver_operations_access_context
#
# Important parameters participants may change:
# - bronze_base
# - silver_base
#
# Plain-language explanation before the code:
# - Read the guide first, then run the code from top to bottom. The early code configures paths and helpers, the middle code builds or transforms data, and the final code writes outputs and prints validation evidence.
#
# Expected row counts or displayed results:
# - The validation display should show 5 district-level records in the workshop sample
# - Displayed fields include capacity_pressure_band, spatial_access_band, residents_per_facility, access_gap_score, and operations_access_risk_score
#
# Safe rerun behaviour:
# - Safe for reruns. The Silver extension output is overwritten without changing the original Claims star schema flow.
#
# Common errors and troubleshooting:
# - Missing JSON/GeoJSON Bronze tables: rerun Bronze and confirm the additional raw formats were uploaded.
# - Null spatial fields: inspect GeoJSON properties and district identifiers.
# - Array-to-CSV issues do not apply here because this notebook writes Delta, not CSV.
#
# What you learned:
# - You learned how to extend an existing lakehouse product with JSON and spatial signals while keeping the original Claims flow stable.
# END PARTICIPANT NOTEBOOK GUIDE
# Public Healthcare AIDP Workshop
# Round 2 extension notebook: Bronze JSON + Spatial -> Silver operations/access context.
#
# Purpose:
# - Demonstrate progressive enhancement after the initial Claims analytics product is live
# - Combine JSON facility capacity events and GeoJSON service-area features
# - Produce one conformed Silver table that can enrich Claims analytics without changing the Claims star schema
#
# Run after:
# - 01_Bronze_Public_Healthcare.ipynb
#
# Output:
# - silver_operations_access_context

from pyspark.sql import functions as F


# -----------------------------------------------------------------------------
# 1. Configure mounted AIDP volume paths.
# This extension reads Bronze JSON and GeoJSON outputs and writes a new Silver
# context table without changing the original Claims star schema flow.
# -----------------------------------------------------------------------------
bronze_base = "/Volumes/e2eindustrydemos/default/e2eindustrydemovol/Bronze"
silver_base = "/Volumes/e2eindustrydemos/default/e2eindustrydemovol/Silver"


# -----------------------------------------------------------------------------
# 2. Shared Delta read/write helpers.
# -----------------------------------------------------------------------------
def read_delta(name):
    return spark.read.format("delta").load(f"{bronze_base}/{name}")


def write_delta(frame, name):
    frame.write.format("delta").mode("overwrite").save(f"{silver_base}/{name}")


# -----------------------------------------------------------------------------
# 3. Load Bronze sources for Round 2 context enrichment.
# Capacity events come from JSONL; service areas come from GeoJSON; facility and
# district references provide the join keys and business labels.
# -----------------------------------------------------------------------------
bronze_capacity_events = read_delta("bronze_facility_capacity_events")
bronze_service_areas = read_delta("bronze_healthcare_service_areas_geojson")
bronze_facility_provider = read_delta("bronze_facility_provider_master")
bronze_district = read_delta("bronze_district_health_profile")


# -----------------------------------------------------------------------------
# 4. Create conformed facility and district reference tables.
# These lookups prevent repeated casting and keep the enrichment joins readable.
# -----------------------------------------------------------------------------
facility_ref = (
    bronze_facility_provider.select(
        "facility_id",
        "facility_name",
        "facility_type",
        "district_id",
        "provider_id",
        "provider_name",
        F.col("licensed_beds").cast("int").alias("licensed_beds"),
        F.col("baseline_daily_visits").cast("int").alias("baseline_daily_visits"),
    )
    .dropDuplicates(["facility_id"])
)


district_ref = (
    bronze_district.select(
        "district_id",
        "district_name",
        F.col("population").cast("int").alias("population"),
        F.col("deprivation_index").cast("double").alias("deprivation_index"),
        F.col("elderly_pct").cast("double").alias("elderly_pct"),
        F.col("chronic_condition_pct").cast("double").alias("chronic_condition_pct"),
        F.col("median_income_usd").cast("int").alias("median_income_usd"),
    )
    .dropDuplicates(["district_id"])
)


# -----------------------------------------------------------------------------
# 5. Parse JSON capacity events into operational signals.
# This section flattens triage counts, counts supply alerts, and labels pressure
# bands so downstream analytics can ask operational questions.
# -----------------------------------------------------------------------------
capacity_events = (
    bronze_capacity_events.select(
        "event_id",
        F.to_timestamp("event_timestamp").alias("event_timestamp"),
        "facility_id",
        F.col("current_occupancy_rate").cast("double").alias("current_occupancy_rate"),
        F.col("waiting_room_count").cast("int").alias("waiting_room_count"),
        F.col("avg_ed_wait_minutes").cast("int").alias("avg_ed_wait_minutes"),
        F.col("triage_category_counts.resuscitation").cast("int").alias("triage_resuscitation"),
        F.col("triage_category_counts.emergent").cast("int").alias("triage_emergent"),
        F.col("triage_category_counts.urgent").cast("int").alias("triage_urgent"),
        F.col("triage_category_counts.standard").cast("int").alias("triage_standard"),
        F.col("supply_alerts").alias("supply_alerts"),
        F.col("ambulance_diversion_status").cast("boolean").alias("ambulance_diversion_status"),
    )
    .withColumn("event_date", F.to_date("event_timestamp"))
    .withColumn("event_hour", F.hour("event_timestamp"))
    .withColumn("event_day_of_week", F.date_format("event_timestamp", "EEEE"))
    .withColumn(
        "triage_total",
        F.coalesce(F.col("triage_resuscitation"), F.lit(0))
        + F.coalesce(F.col("triage_emergent"), F.lit(0))
        + F.coalesce(F.col("triage_urgent"), F.lit(0))
        + F.coalesce(F.col("triage_standard"), F.lit(0)),
    )
    .withColumn("supply_alert_count", F.when(F.col("supply_alerts").isNull(), F.lit(0)).otherwise(F.size("supply_alerts")))
    .withColumn("diversion_event_flag", F.when(F.col("ambulance_diversion_status") == F.lit(True), F.lit("Y")).otherwise(F.lit("N")))
    .withColumn(
        "critical_supply_flag",
        F.when(F.col("supply_alert_count") >= 2, F.lit("Y")).otherwise(F.lit("N")),
    )
    .withColumn(
        "triage_acuity_score",
        F.coalesce(F.col("triage_resuscitation"), F.lit(0)) * F.lit(5.0)
        + F.coalesce(F.col("triage_emergent"), F.lit(0)) * F.lit(4.0)
        + F.coalesce(F.col("triage_urgent"), F.lit(0)) * F.lit(2.0)
        + F.coalesce(F.col("triage_standard"), F.lit(0)) * F.lit(1.0),
    )
    .withColumn(
        "capacity_pressure_band",
        F.when((F.col("current_occupancy_rate") >= 0.95) | (F.col("avg_ed_wait_minutes") >= 75), F.lit("High"))
        .when((F.col("current_occupancy_rate") >= 0.85) | (F.col("avg_ed_wait_minutes") >= 60), F.lit("Medium"))
        .otherwise(F.lit("Watch")),
    )
)


# -----------------------------------------------------------------------------
# 6. Flatten GeoJSON features and flag spatial quality.
# The geometry is retained as GeoJSON text while each feature is tagged as
# usable or needing review.
# -----------------------------------------------------------------------------
spatial_features = (
    bronze_service_areas.select(F.explode("features").alias("feature"))
    .select(
        F.col("feature.properties.source_layer").alias("source_layer"),
        F.col("feature.properties.district_id").alias("district_id"),
        F.col("feature.properties.facility_id").alias("facility_id"),
        F.col("feature.properties.facility_name").alias("spatial_facility_name"),
        F.col("feature.geometry.type").alias("geometry_type"),
        F.to_json("feature.geometry").alias("geometry_geojson"),
    )
    .withColumn("has_geometry_flag", F.when(F.col("geometry_geojson").isNotNull(), F.lit("Y")).otherwise(F.lit("N")))
    .withColumn(
        "spatial_quality_status",
        F.when(F.col("district_id").isNull() | (F.col("has_geometry_flag") == "N"), F.lit("Review"))
        .otherwise(F.lit("Valid")),
    )
)


# -----------------------------------------------------------------------------
# 7. Aggregate spatial features to district access context.
# These counts support map-style questions such as coverage gaps and mapped
# facilities per district.
# -----------------------------------------------------------------------------
spatial_district_context = (
    spatial_features.groupBy("district_id")
    .agg(
        F.count("*").alias("spatial_feature_count"),
        F.countDistinct(F.when(F.col("source_layer") == "facility_catchment", F.col("facility_id"))).alias("catchment_count"),
        F.countDistinct(F.when(F.col("source_layer") == "facility_point", F.col("facility_id"))).alias("mapped_facility_count"),
        F.max(F.when(F.col("source_layer") == "district_boundary", F.lit(1)).otherwise(F.lit(0))).alias("has_district_boundary"),
        F.sum(F.when(F.col("spatial_quality_status") == "Review", F.lit(1)).otherwise(F.lit(0))).alias("spatial_quality_review_count"),
    )
)


# -----------------------------------------------------------------------------
# 8. Calculate district-level access-gap indicators.
# Residents per facility, catchment coverage, and deprivation combine into a
# simple access-gap score for claims-context enrichment.
# -----------------------------------------------------------------------------
facility_district_counts = (
    facility_ref.groupBy("district_id")
    .agg(
        F.countDistinct("facility_id").alias("facility_count"),
        F.countDistinct("provider_id").alias("provider_count"),
    )
)


district_access_context = (
    district_ref.join(facility_district_counts, "district_id", "left")
    .join(spatial_district_context, "district_id", "left")
    .withColumn("facility_count", F.coalesce(F.col("facility_count"), F.lit(0)))
    .withColumn("provider_count", F.coalesce(F.col("provider_count"), F.lit(0)))
    .withColumn("catchment_count", F.coalesce(F.col("catchment_count"), F.lit(0)))
    .withColumn("mapped_facility_count", F.coalesce(F.col("mapped_facility_count"), F.lit(0)))
    .withColumn(
        "residents_per_facility",
        F.when(F.col("facility_count") > 0, F.round(F.col("population") / F.col("facility_count"), 0)).otherwise(F.lit(None)),
    )
    .withColumn(
        "spatial_access_band",
        F.when((F.col("residents_per_facility") >= 30000) | (F.col("catchment_count") < F.col("facility_count")), F.lit("High Gap"))
        .when((F.col("residents_per_facility") >= 20000) | (F.col("deprivation_index") >= 0.65), F.lit("Watch"))
        .otherwise(F.lit("Adequate")),
    )
    .withColumn(
        "access_gap_score",
        F.round(
            F.least(
                F.lit(100.0),
                F.coalesce(F.col("deprivation_index"), F.lit(0.0)) * F.lit(45.0)
                + F.coalesce(F.col("residents_per_facility"), F.lit(0.0)) / F.lit(900.0)
                + F.when(F.col("catchment_count") < F.col("facility_count"), F.lit(18.0)).otherwise(F.lit(0.0)),
            ),
            1,
        ),
    )
)


# -----------------------------------------------------------------------------
# 9. Build the final Silver operations/access context table.
# This table combines JSON event pressure and spatial access signals at the
# facility-event grain, ready for Gold monthly aggregation.
# -----------------------------------------------------------------------------
silver_operations_access_context = (
    capacity_events.join(facility_ref, "facility_id", "left")
    .join(district_access_context, "district_id", "left")
    .withColumn(
        "operations_access_risk_score",
        F.round(
            F.least(
                F.lit(100.0),
                F.coalesce(F.col("current_occupancy_rate"), F.lit(0.0)) * F.lit(35.0)
                + F.coalesce(F.col("avg_ed_wait_minutes"), F.lit(0)) * F.lit(0.35)
                + F.coalesce(F.col("supply_alert_count"), F.lit(0)) * F.lit(4.0)
                + F.when(F.col("diversion_event_flag") == "Y", F.lit(10.0)).otherwise(F.lit(0.0))
                + F.coalesce(F.col("access_gap_score"), F.lit(0.0)) * F.lit(0.25),
            ),
            1,
        ),
    )
    .select(
        "event_id",
        "event_timestamp",
        "event_date",
        "event_hour",
        "event_day_of_week",
        "district_id",
        "district_name",
        "facility_id",
        "facility_name",
        "facility_type",
        "provider_id",
        "provider_name",
        "current_occupancy_rate",
        "waiting_room_count",
        "avg_ed_wait_minutes",
        "triage_resuscitation",
        "triage_emergent",
        "triage_urgent",
        "triage_standard",
        "triage_total",
        "triage_acuity_score",
        "supply_alert_count",
        "diversion_event_flag",
        "critical_supply_flag",
        "capacity_pressure_band",
        "population",
        "deprivation_index",
        "facility_count",
        "provider_count",
        "catchment_count",
        "mapped_facility_count",
        "residents_per_facility",
        "spatial_access_band",
        "access_gap_score",
        "operations_access_risk_score",
    )
)


# -----------------------------------------------------------------------------
# 10. Persist and display a compact validation summary.
# The group-by output gives the instructor an immediate smoke test after the
# notebook finishes.
# -----------------------------------------------------------------------------
write_delta(silver_operations_access_context, "silver_operations_access_context")

print("Round 2 Silver context complete.")
print(f"Wrote silver_operations_access_context to {silver_base}/silver_operations_access_context")
silver_operations_access_context.groupBy("district_name", "capacity_pressure_band", "spatial_access_band").count().orderBy(
    "district_name", "capacity_pressure_band", "spatial_access_band"
).show(50, truncate=False)
