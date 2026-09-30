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
# # 02 Silver - Conform MPHA Operational Context
#
# ## What this section does and why it matters
# Reads Bronze Delta folders, types and cleans raw fields, standardizes entities, derives operational flags, and publishes reusable Silver Delta tables.
#
# **Why it matters:** Silver is where MPHA decides whether the data can be trusted across claims, provider, facility, membership, public-health, JSON, and spatial use cases.
#
# ## Inputs and outputs
#
# **Inputs**
# - Bronze Delta folders from the Bronze notebook
#
# **Outputs**
# - Silver district, facility/provider, facility-day, population-health, claims, accreditation, JSON capacity, spatial feature, and document-context tables under `<output_base>/silver`
#
# ## Important parameters participants may change
# - `volume_base`
# - `participant_id`
# - `bronze_base`
# - `silver_base`
# - `risk_reference_date`

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
# Silver notebook: Bronze Delta tables -> typed, conformed Silver Delta tables in AIDP.
#
# Run `aidp_bronze_pyspark.py` first so the Bronze tables exist.

from pyspark.sql import functions as F


# %% [markdown]
# ## Code section - Configure Bronze input and Silver output paths
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 1. Configure Bronze input and Silver output paths.
# Silver is where raw strings and nested JSON become typed, business-friendly
# tables that can safely feed Gold, ML, and OAC. Use the same participant_id
# used in the Bronze notebook so this notebook reads your Bronze output and
# writes your own Silver output.
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

bronze_base = f"{output_base}/bronze"
silver_base = f"{output_base}/silver"
risk_reference_date = F.to_date(F.lit("2025-06-30"))


# %% [markdown]
# ## Code section - Shared helpers
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 2. Shared helpers.
# `safe_rate` avoids divide-by-zero errors while still returning a numeric value
# that downstream dashboards and models can consume.
# -----------------------------------------------------------------------------
def read_delta(name):
    return spark.read.format("delta").load(f"{bronze_base}/{name}")


def write_delta(frame, name):
    frame.write.format("delta").mode("overwrite").save(f"{silver_base}/{name}")


def safe_rate(numerator, denominator):
    return F.when(F.col(denominator) > 0, F.col(numerator) / F.col(denominator)).otherwise(F.lit(0.0))


# %% [markdown]
# ## Code section - Load all Bronze inputs produced by the Bronze notebook
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 3. Load all Bronze inputs produced by the Bronze notebook.
# The JSON capacity events and GeoJSON service areas remain nested until their
# dedicated Silver transformations below.
# -----------------------------------------------------------------------------
bronze_district_health_profile = read_delta("bronze_district_health_profile")
bronze_facility_provider_master = read_delta("bronze_facility_provider_master")
bronze_facility_operations_daily = read_delta("bronze_facility_operations_daily")
bronze_population_health_weekly = read_delta("bronze_population_health_weekly")
bronze_claims_membership_disbursement = read_delta("bronze_claims_membership_disbursement")
bronze_facility_capacity_events = read_delta("bronze_facility_capacity_events")
bronze_healthcare_service_areas_geojson = read_delta("bronze_healthcare_service_areas_geojson")


# %% [markdown]
# ## Code section - Conform district reference data
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 4. Conform district reference data.
# This becomes the common district lookup for facility, claims, population, and
# spatial analytics.
# -----------------------------------------------------------------------------
silver_district = (
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


# %% [markdown]
# ## Code section - Conform facilities, providers, and accreditation attributes
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 5. Conform facilities, providers, and accreditation attributes.
# The join to district adds local public-health context to each provider row.
# -----------------------------------------------------------------------------
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
    .join(silver_district, "district_id", "left")
    .dropDuplicates(["facility_id"])
)


# %% [markdown]
# ## Code section - Clean daily facility operations and derive access-risk signals
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 6. Clean daily facility operations and derive access-risk signals.
# This step standardizes negative or out-of-range operational measures and
# calculates wait-time variance, occupancy flags, and an access risk score.
# -----------------------------------------------------------------------------
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
    .join(
        silver_facility_provider.select(
            "facility_id",
            "district_id",
            "facility_type",
            "target_ed_wait_minutes",
            "target_outpatient_wait_minutes",
            "deprivation_index",
        ),
        "facility_id",
        "left",
    )
    .withColumn(
        "ed_wait_variance_minutes",
        F.when(F.col("target_ed_wait_minutes") > 0, F.col("avg_ed_wait_minutes") - F.col("target_ed_wait_minutes")).otherwise(F.lit(0)),
    )
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


# %% [markdown]
# ## Code section - Clean population-health weekly measures
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 7. Clean population-health weekly measures.
# These fields support equity and public-health pressure calculations.
# -----------------------------------------------------------------------------
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


# %% [markdown]
# ## Code section - Aggregate district-week public-health pressure
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 8. Aggregate district-week public-health pressure.
# The pressure index blends positivity, appointment no-shows, deprivation, and
# immunization completion into a single signal for planning.
# -----------------------------------------------------------------------------
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
    .join(silver_district, "district_id", "left")
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


# %% [markdown]
# ## Code section - Clean claims, membership, and disbursement data
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 9. Clean claims, membership, and disbursement data.
# This is the main payer-side table used by the Claims star schema and ML lab.
# -----------------------------------------------------------------------------
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


# %% [markdown]
# ## Code section - Derive provider-accreditation pressure
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 10. Derive provider-accreditation pressure.
# `days_to_expiry` and corrective actions turn accreditation metadata into a
# business-friendly risk band.
# -----------------------------------------------------------------------------
silver_provider_accreditation = (
    silver_facility_provider.select(
        "facility_id",
        "facility_name",
        "provider_id",
        "provider_name",
        "district_id",
        "district_name",
        "facility_type",
        "accreditation_body",
        "accreditation_status",
        "accreditation_level",
        "last_survey_date",
        "expiry_date",
        "accreditation_score",
        "corrective_action_count",
        "specialty_scope",
    )
    .withColumn("days_to_expiry", F.datediff(F.col("expiry_date"), risk_reference_date))
    .withColumn(
        "accreditation_pressure_band",
        F.when((F.col("days_to_expiry") <= 30) | (F.col("corrective_action_count") >= 3), "High")
        .when((F.col("days_to_expiry") <= 90) | (F.col("corrective_action_count") >= 1), "Medium")
        .otherwise("Watch"),
    )
)


# %% [markdown]
# ## Code section - Parse the JSON facility-capacity events
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 11. Parse the JSON facility-capacity events.
# Nested triage counts and supply alerts become structured columns that can be
# used in Round 2 context enrichment and ML scoring.
# -----------------------------------------------------------------------------
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


# %% [markdown]
# ## Code section - Flatten GeoJSON service-area features
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 12. Flatten GeoJSON service-area features.
# The geometry is retained as GeoJSON text so it can be loaded into spatial
# tooling while the properties are exposed for joins.
# -----------------------------------------------------------------------------
silver_spatial_feature = (
    bronze_healthcare_service_areas_geojson.select(F.explode("features").alias("feature"))
    .select(
        F.col("feature.properties.source_layer").alias("source_layer"),
        F.col("feature.properties.district_id").alias("district_id"),
        F.col("feature.properties.facility_id").alias("facility_id"),
        F.col("feature.properties.facility_name").alias("facility_name"),
        F.to_json("feature.geometry").alias("geometry_geojson"),
    )
)


# %% [markdown]
# ## Code section - Register all Silver outputs in one write map
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 13. Register all Silver outputs in one write map.
# Keeping the write list together makes it easy to audit what this notebook
# creates and what downstream notebooks can consume.
# -----------------------------------------------------------------------------
silver_tables = {
    "silver_district": silver_district,
    "silver_facility_provider": silver_facility_provider,
    "silver_facility_day": silver_facility_day,
    "silver_population_health_week": silver_population_health_week,
    "silver_district_health_week": silver_district_health_week,
    "silver_claims_membership_disbursement": silver_claims_membership_disbursement,
    "silver_provider_accreditation": silver_provider_accreditation,
    "silver_facility_capacity_event": silver_facility_capacity_event,
    "silver_spatial_feature": silver_spatial_feature,
}


# %% [markdown]
# ## Code section - Persist Silver Delta tables and print the completion handoff
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 14. Persist Silver Delta tables and print the completion handoff.
# -----------------------------------------------------------------------------
for table_name, frame in silver_tables.items():
    write_delta(frame, table_name)
    print(f"Wrote {table_name} to {silver_base}/{table_name}")


print(
    "Silver layer complete. Use your document-vector tooling to create silver_playbook_chunk if you want playbook chunks stored beside the Delta outputs."
)


# %% [markdown]
# ## Expected row counts or displayed results
# - Silver row counts should broadly match source grains: 5 districts, 10 facilities, 1,810 facility-days, 780 weekly population rows, and 1,400 claims rows
# - Derived displays should show access risk, public-health pressure, denial rates, accreditation bands, JSON capacity fields, and spatial access context
#
# ## Safe rerun behaviour
# Safe for repeat classroom runs. Silver outputs are overwritten from Bronze, so downstream notebooks should be rerun after a Silver rerun.
#
# ## Common errors and troubleshooting
# - Missing Bronze table: rerun Bronze and verify bronze_base.
# - Unexpected nulls after casts: inspect raw CSV values and confirm headers were not modified.
# - Duplicate or ambiguous columns: keep the selected Silver joins and aliases unchanged.

# %% [markdown]
# ## What you learned
# You learned how raw operational signals become trusted, typed, and reusable Silver data products.
