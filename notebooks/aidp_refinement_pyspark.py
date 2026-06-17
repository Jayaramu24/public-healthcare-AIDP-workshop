# Public Healthcare AIDP Workshop
# AIDP medallion notebook: simplified raw sources -> Bronze -> Silver -> AI Lakehouse Gold
#
# Preferred workshop flow:
#   notebooks/aidp_bronze_pyspark.py
#   notebooks/aidp_silver_pyspark.py
#   notebooks/aidp_gold_pyspark.py
# This combined file is kept as a legacy single-script reference.
#
# Source contract:
#   5 CSV datasets, 1 JSON dataset, 1 spatial dataset, 1 document.
# Set the paths to your Object Storage or mounted lakehouse locations.

from pyspark.sql import functions as F


raw_base = "oci://<bucket>@<namespace>/mpha/raw"
raw_json_base = "oci://<bucket>@<namespace>/mpha/raw_json"
raw_spatial_base = "oci://<bucket>@<namespace>/mpha/raw_spatial"
document_base = "oci://<bucket>@<namespace>/mpha/documents"
bronze_base = "oci://<bucket>@<namespace>/mpha/bronze"
silver_base = "oci://<bucket>@<namespace>/mpha/silver"
gold_stage_base = "oci://<bucket>@<namespace>/mpha/gold_stage"
ingest_batch_id = "mpha_2025_h1_simplified_workshop"


def read_raw_csv(name):
    return (
        spark.read.option("header", "true")
        .option("inferSchema", "false")
        .csv(f"{raw_base}/{name}.csv")
    )


def read_json_lines(base, name):
    return spark.read.option("multiLine", "false").json(f"{base}/{name}")


def read_json_document(base, name):
    return spark.read.option("multiLine", "true").json(f"{base}/{name}")


def add_bronze_metadata(frame):
    return (
        frame.withColumn("_source_file", F.input_file_name())
        .withColumn("_ingest_batch_id", F.lit(ingest_batch_id))
        .withColumn("_ingested_at", F.current_timestamp())
    )


def write_delta(frame, path, partition_cols=None):
    writer = frame.write.format("delta").mode("overwrite")
    if partition_cols:
        writer = writer.partitionBy(*partition_cols)
    writer.save(path)


def safe_rate(numerator, denominator):
    return F.when(F.col(denominator) > 0, F.col(numerator) / F.col(denominator)).otherwise(F.lit(0.0))


# Bronze: keep source values intact and add ingestion metadata.
bronze_district_health_profile = add_bronze_metadata(read_raw_csv("district_health_profile"))
bronze_facility_provider_master = add_bronze_metadata(read_raw_csv("facility_provider_master"))
bronze_facility_operations_daily = add_bronze_metadata(read_raw_csv("facility_operations_daily"))
bronze_population_health_weekly = add_bronze_metadata(read_raw_csv("population_health_weekly"))
bronze_claims_membership_disbursement = add_bronze_metadata(read_raw_csv("claims_membership_disbursement"))
bronze_facility_capacity_events = add_bronze_metadata(read_json_lines(raw_json_base, "facility_capacity_events.jsonl"))
bronze_healthcare_service_areas = add_bronze_metadata(read_json_document(raw_spatial_base, "healthcare_service_areas.geojson"))

write_delta(bronze_district_health_profile, f"{bronze_base}/bronze_district_health_profile")
write_delta(bronze_facility_provider_master, f"{bronze_base}/bronze_facility_provider_master")
write_delta(bronze_facility_operations_daily, f"{bronze_base}/bronze_facility_operations_daily")
write_delta(bronze_population_health_weekly, f"{bronze_base}/bronze_population_health_weekly")
write_delta(bronze_claims_membership_disbursement, f"{bronze_base}/bronze_claims_membership_disbursement")
write_delta(bronze_facility_capacity_events, f"{bronze_base}/bronze_facility_capacity_events")
write_delta(bronze_healthcare_service_areas, f"{bronze_base}/bronze_healthcare_service_areas_geojson")


# Silver: typed, validated, conformed Delta tables in AIDP.
district = (
    bronze_district_health_profile.select(
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

silver_facility_provider = (
    bronze_facility_provider_master.select(
        "facility_id",
        "facility_name",
        F.initcap("facility_type").alias("facility_type"),
        "district_id",
        F.col("latitude").cast("double").alias("latitude"),
        F.col("longitude").cast("double").alias("longitude"),
        F.col("licensed_beds").cast("int").alias("licensed_beds"),
        F.col("baseline_daily_visits").cast("int").alias("baseline_daily_visits"),
        F.col("target_ed_wait_minutes").cast("int").alias("target_ed_wait_minutes"),
        F.col("target_outpatient_wait_minutes").cast("int").alias("target_outpatient_wait_minutes"),
        "provider_id",
        "provider_name",
        "accreditation_body",
        F.initcap("accreditation_status").alias("accreditation_status"),
        "accreditation_level",
        F.to_date("last_survey_date").alias("last_survey_date"),
        F.to_date("expiry_date").alias("expiry_date"),
        F.col("accreditation_score").cast("double").alias("accreditation_score"),
        F.col("corrective_action_count").cast("int").alias("corrective_action_count"),
        "specialty_scope",
    )
    .join(district, "district_id", "left")
    .dropDuplicates(["facility_id"])
)

silver_facility_day = (
    bronze_facility_operations_daily.select(
        F.to_date("service_date").alias("service_date"),
        "facility_id",
        F.greatest(F.col("outpatient_visits").cast("int"), F.lit(0)).alias("outpatient_visits"),
        F.greatest(F.col("emergency_arrivals").cast("int"), F.lit(0)).alias("emergency_arrivals"),
        F.greatest(F.col("admissions").cast("int"), F.lit(0)).alias("admissions"),
        F.greatest(F.col("discharges").cast("int"), F.lit(0)).alias("discharges"),
        F.greatest(F.col("avg_ed_wait_minutes").cast("int"), F.lit(0)).alias("avg_ed_wait_minutes"),
        F.greatest(F.col("avg_outpatient_wait_minutes").cast("int"), F.lit(0)).alias("avg_outpatient_wait_minutes"),
        F.least(F.greatest(F.col("no_show_rate").cast("double"), F.lit(0.0)), F.lit(1.0)).alias("no_show_rate"),
        F.least(F.greatest(F.col("bed_occupancy_rate").cast("double"), F.lit(0.0)), F.lit(1.25)).alias("bed_occupancy_rate"),
        F.greatest(F.col("staff_hours").cast("double"), F.lit(0.0)).alias("staff_hours"),
        F.greatest(F.col("overtime_hours").cast("double"), F.lit(0.0)).alias("overtime_hours"),
        F.least(F.greatest(F.col("patient_satisfaction_score").cast("double"), F.lit(0.0)), F.lit(100.0)).alias("patient_satisfaction_score"),
        F.greatest(F.col("quality_event_count").cast("int"), F.lit(0)).alias("quality_event_count"),
        F.greatest(F.col("high_severity_quality_events").cast("int"), F.lit(0)).alias("high_severity_quality_events"),
        F.greatest(F.col("avg_days_to_close_quality_events").cast("double"), F.lit(0.0)).alias("avg_days_to_close_quality_events"),
        F.greatest(F.col("avoidable_readmission_events").cast("int"), F.lit(0)).alias("avoidable_readmission_events"),
    )
    .join(silver_facility_provider.select("facility_id", "district_id", "facility_type", "target_ed_wait_minutes", "target_outpatient_wait_minutes", "deprivation_index"), "facility_id", "left")
    .withColumn("ed_wait_variance_minutes", F.when(F.col("target_ed_wait_minutes") > 0, F.col("avg_ed_wait_minutes") - F.col("target_ed_wait_minutes")).otherwise(F.lit(0)))
    .withColumn("outpatient_wait_variance_minutes", F.col("avg_outpatient_wait_minutes") - F.col("target_outpatient_wait_minutes"))
    .withColumn("high_occupancy_flag", F.when(F.col("bed_occupancy_rate") >= 0.90, "Y").otherwise("N"))
    .withColumn(
        "access_risk_score",
        F.round(
            F.least(
                F.lit(100.0),
                F.col("deprivation_index") * F.lit(35.0)
                + F.greatest(F.lit(0.0), F.col("outpatient_wait_variance_minutes")) * F.lit(0.45)
                + F.greatest(F.lit(0.0), F.col("ed_wait_variance_minutes")) * F.lit(0.22)
                + F.col("no_show_rate") * F.lit(120.0),
            ),
            1,
        ),
    )
)

silver_population_health_week = (
    bronze_population_health_weekly.select(
        F.to_date("week_start_date").alias("week_start_date"),
        "district_id",
        "age_group",
        F.greatest(F.col("eligible_population").cast("int"), F.lit(0)).alias("eligible_population"),
        F.greatest(F.col("appointments_booked").cast("int"), F.lit(0)).alias("appointments_booked"),
        F.greatest(F.col("missed_appointments").cast("int"), F.lit(0)).alias("missed_appointments"),
        F.greatest(F.col("walk_in_visits").cast("int"), F.lit(0)).alias("walk_in_visits"),
        F.greatest(F.col("doses_administered").cast("int"), F.lit(0)).alias("doses_administered"),
        F.greatest(F.col("tests_reported").cast("int"), F.lit(0)).alias("tests_reported"),
        F.greatest(F.col("positive_tests").cast("int"), F.lit(0)).alias("positive_tests"),
        F.least(F.greatest(F.col("positivity_rate").cast("double"), F.lit(0.0)), F.lit(1.0)).alias("positivity_rate"),
        F.greatest(F.col("respiratory_related_ed_visits").cast("int"), F.lit(0)).alias("respiratory_related_ed_visits"),
    )
    .withColumn("completion_rate", F.round(safe_rate("doses_administered", "eligible_population"), 4))
    .withColumn("immunization_no_show_rate", F.round(safe_rate("missed_appointments", "appointments_booked"), 4))
)

silver_district_health_week = (
    silver_population_health_week.groupBy("week_start_date", "district_id")
    .agg(
        F.sum("eligible_population").alias("eligible_population"),
        F.sum("appointments_booked").alias("appointments_booked"),
        F.sum("missed_appointments").alias("missed_appointments"),
        F.sum("doses_administered").alias("doses_administered"),
        F.max("tests_reported").alias("tests_reported"),
        F.max("positive_tests").alias("positive_tests"),
        F.max("positivity_rate").alias("positivity_rate"),
        F.max("respiratory_related_ed_visits").alias("respiratory_related_ed_visits"),
    )
    .join(district, "district_id", "left")
    .withColumn("completion_rate", F.round(safe_rate("doses_administered", "eligible_population"), 4))
    .withColumn("immunization_no_show_rate", F.round(safe_rate("missed_appointments", "appointments_booked"), 4))
    .withColumn(
        "public_health_pressure_index",
        F.round(
            F.least(
                F.lit(100.0),
                F.col("positivity_rate") * F.lit(240.0)
                + F.col("immunization_no_show_rate") * F.lit(120.0)
                + F.col("deprivation_index") * F.lit(32.0)
                - F.col("completion_rate") * F.lit(45.0),
            ),
            1,
        ),
    )
)

silver_claims_membership_disbursement = (
    bronze_claims_membership_disbursement.select(
        "claim_id",
        "member_id",
        "facility_id",
        "provider_id",
        "district_id",
        F.to_date("service_date").alias("service_date"),
        F.to_date("claim_received_date").alias("claim_received_date"),
        "program_code",
        "coverage_program",
        "program_type",
        "funding_source",
        "claim_type",
        "service_category",
        "diagnosis_group",
        F.greatest(F.col("submitted_amount").cast("double"), F.lit(0.0)).alias("submitted_amount"),
        F.greatest(F.col("approved_amount").cast("double"), F.lit(0.0)).alias("approved_amount"),
        F.greatest(F.col("paid_amount").cast("double"), F.lit(0.0)).alias("paid_amount"),
        F.initcap("claim_status").alias("claim_status"),
        "denial_reason",
        F.greatest(F.col("processing_days").cast("int"), F.lit(0)).alias("processing_days"),
        F.to_date("enrollment_date").alias("enrollment_date"),
        F.to_date("renewal_due_date").alias("renewal_due_date"),
        F.initcap("eligibility_status").alias("eligibility_status"),
        "age_group",
        F.initcap("risk_segment").alias("risk_segment"),
        F.when(F.upper("chronic_condition_flag") == "Y", "Y").otherwise("N").alias("chronic_condition_flag"),
        "disbursement_id",
        "payee_type",
        F.to_date("disbursement_date").alias("disbursement_date"),
        F.greatest(F.col("disbursement_amount").cast("double"), F.lit(0.0)).alias("disbursement_amount"),
        "payment_method",
        F.initcap("payment_status").alias("payment_status"),
        F.col("payment_cycle_days").cast("int").alias("payment_cycle_days"),
    )
    .dropDuplicates(["claim_id"])
)

silver_facility_capacity_event = (
    bronze_facility_capacity_events.select(
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
    .withColumn("triage_total", F.col("triage_resuscitation") + F.col("triage_emergent") + F.col("triage_urgent") + F.col("triage_standard"))
    .withColumn("supply_alert_count", F.size("supply_alerts"))
    .withColumn(
        "capacity_pressure_band",
        F.when((F.col("current_occupancy_rate") >= 0.95) | (F.col("avg_ed_wait_minutes") >= 75), "High")
        .when((F.col("current_occupancy_rate") >= 0.85) | (F.col("avg_ed_wait_minutes") >= 60), "Medium")
        .otherwise("Watch"),
    )
)

silver_spatial_feature = (
    bronze_healthcare_service_areas.select(F.explode("features").alias("feature"))
    .select(
        F.col("feature.properties.source_layer").alias("source_layer"),
        F.col("feature.properties.district_id").alias("district_id"),
        F.col("feature.properties.facility_id").alias("facility_id"),
        F.col("feature.properties.facility_name").alias("facility_name"),
        F.to_json("feature.geometry").alias("geometry_geojson"),
    )
)

for name, frame in {
    "silver_district": district,
    "silver_facility_provider": silver_facility_provider,
    "silver_facility_day": silver_facility_day,
    "silver_population_health_week": silver_population_health_week,
    "silver_district_health_week": silver_district_health_week,
    "silver_claims_membership_disbursement": silver_claims_membership_disbursement,
    "silver_facility_capacity_event": silver_facility_capacity_event,
    "silver_spatial_feature": silver_spatial_feature,
}.items():
    write_delta(frame, f"{silver_base}/{name}")


# Gold examples staged for AI Lakehouse loading.
gold_facility_access_daily = (
    silver_facility_day.alias("f")
    .join(silver_facility_provider.select("facility_id", "facility_name", "district_name").alias("d"), "facility_id", "left")
)

gold_district_public_health_weekly = silver_district_health_week
gold_immunization_equity_weekly = silver_population_health_week.join(district.select("district_id", "district_name", "deprivation_index", "elderly_pct"), "district_id", "left")
gold_claims_summary = (
    silver_claims_membership_disbursement.withColumn("service_month", F.to_date(F.date_format("service_date", "yyyy-MM-01")))
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
    .withColumn("denial_rate", F.round(F.col("denied_claims") / F.greatest(F.col("claims_submitted"), F.lit(1)), 4))
)

for name, frame in {
    "gold_facility_access_daily": gold_facility_access_daily,
    "gold_district_public_health_weekly": gold_district_public_health_weekly,
    "gold_immunization_equity_weekly": gold_immunization_equity_weekly,
    "gold_claims_summary": gold_claims_summary,
}.items():
    frame.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{gold_stage_base}/{name}")

print("Simplified AIDP medallion flow complete.")
