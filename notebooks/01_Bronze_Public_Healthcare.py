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
# # 01 Bronze - Land MPHA Raw Signals
#
# ## What this section does and why it matters
# Loads the five CSV files, one JSONL event extract, and one GeoJSON document into Bronze Delta folders while preserving source fidelity and adding ingestion metadata.
#
# **Why it matters:** Bronze is the audit and replay layer. It lets participants explain exactly which raw operational signals entered the workshop before any cleansing or business rules are applied.
#
# ## Inputs and outputs
#
# **Inputs**
# - Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/raw/*.csv
# - Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/raw_json/facility_capacity_events.jsonl
# - Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/raw_spatial/healthcare_service_areas.geojson
# - Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/documents/MPHA_Winter_Respiratory_Response_Playbook.docx remains available for RAG
#
# **Outputs**
# - 7 Bronze Delta folders under `<output_base>/bronze`
# - The playbook document remains available for the later RAG knowledge-base lab
#
# ## Important parameters participants may change
# - `volume_base`
# - `participant_id`
# - `raw_base, raw_json_base, raw_spatial_base, document_base, bronze_base`
# - `ingest_batch_id`

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
# Bronze notebook: simplified raw sources -> Bronze Delta tables in AIDP.
#
# This notebook uses the shared AIDP external volume created in Lab 0.
# Change only `participant_id` so each participant writes to their own area.

from pyspark.sql import functions as F


# %% [markdown]
# ## Code section - Configure landing-zone and Bronze-layer paths
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 1. Configure landing-zone and Bronze-layer paths.
# All participants read the same shared raw data folders. Each participant writes
# Bronze output under their own workshop_runs/<participant_id> prefix so nobody
# overwrites another participant's work.
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

raw_base = f"{volume_base}/raw"
raw_json_base = f"{volume_base}/raw_json"
raw_spatial_base = f"{volume_base}/raw_spatial"
document_base = f"{volume_base}/documents"
bronze_base = f"{output_base}/bronze"
ingest_batch_id = "mpha_2025_h1_simplified_workshop"


# %% [markdown]
# ## Code section - Read helpers for each supported raw format
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 2. Read helpers for each supported raw format.
# CSV inputs are kept as strings in Bronze; JSONL and GeoJSON are read with the
# native Spark JSON reader so nested fields remain available for Silver parsing.
# -----------------------------------------------------------------------------
def read_raw_csv(name):
    return (
        spark.read.option("header", "true")
        .option("inferSchema", "false")
        .csv(f"{raw_base}/{name}.csv")
    )


def read_json_lines(name):
    return spark.read.option("multiLine", "false").json(f"{raw_json_base}/{name}.jsonl")


def read_geojson_document(name):
    return spark.read.option("multiLine", "true").json(f"{raw_spatial_base}/{name}.geojson")


# %% [markdown]
# ## Code section - Bronze metadata and Delta writer
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 3. Bronze metadata and Delta writer.
# Bronze should preserve source values while adding operational lineage columns
# that help participants explain where each row came from.
# -----------------------------------------------------------------------------
def add_bronze_metadata(frame):
    return (
        frame.withColumn("_source_file", F.input_file_name())
        .withColumn("_ingest_batch_id", F.lit(ingest_batch_id))
        .withColumn("_ingested_at", F.current_timestamp())
    )


def write_delta(frame, name):
    frame.write.format("delta").mode("overwrite").save(f"{bronze_base}/{name}")


# %% [markdown]
# ## Code section - Create the Bronze tables
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 4. Create the Bronze tables.
# The workshop intentionally uses five CSV files, one JSONL event stream extract,
# one GeoJSON spatial file, and one document kept in the landing zone for RAG.
# -----------------------------------------------------------------------------
bronze_tables = {
    "bronze_district_health_profile": add_bronze_metadata(read_raw_csv("district_health_profile")),
    "bronze_facility_provider_master": add_bronze_metadata(read_raw_csv("facility_provider_master")),
    "bronze_facility_operations_daily": add_bronze_metadata(read_raw_csv("facility_operations_daily")),
    "bronze_population_health_weekly": add_bronze_metadata(read_raw_csv("population_health_weekly")),
    "bronze_claims_membership_disbursement": add_bronze_metadata(read_raw_csv("claims_membership_disbursement")),
    "bronze_facility_capacity_events": add_bronze_metadata(read_json_lines("facility_capacity_events")),
    "bronze_healthcare_service_areas_geojson": add_bronze_metadata(read_geojson_document("healthcare_service_areas")),
}


# %% [markdown]
# ## Code section - Persist Bronze outputs
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 5. Persist Bronze outputs.
# Downstream Silver notebooks read these Delta folders by table name.
# -----------------------------------------------------------------------------
for table_name, frame in bronze_tables.items():
    write_delta(frame, table_name)
    print(f"Wrote {table_name} to {bronze_base}/{table_name}")


# %% [markdown]
# ## Code section - Handoff checkpoint
# This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.

# %%
# -----------------------------------------------------------------------------
# 6. Handoff checkpoint.
# The document is not converted to Delta here; it is consumed later by the
# document-vector / RAG knowledge-base flow.
# -----------------------------------------------------------------------------
print(
    "Bronze layer complete. The healthcare playbook document remains in the landing zone for the document-vector workflow:",
    f"{document_base}/MPHA_Winter_Respiratory_Response_Playbook.docx",
)


# %% [markdown]
# ## Expected row counts or displayed results
# - district profile: 5 rows
# - facility/provider master: 10 rows
# - facility operations daily: 1,810 rows
# - population health weekly: 780 rows
# - claims/membership/disbursement: 1,400 rows
# - facility capacity events: 80 rows
# - GeoJSON service areas: 25 features
#
# ## Safe rerun behaviour
# Safe for classroom reruns. The notebook overwrites Bronze Delta folders and preserves the current source snapshot with a fresh ingestion timestamp.
#
# ## Common errors and troubleshooting
# - Path or authorization errors: verify bucket, namespace, policies, and external volume access.
# - Empty CSV outputs: confirm files were uploaded under mpha/raw and include headers.
# - JSON or GeoJSON parsing issues: confirm the JSONL and GeoJSON files were uploaded to the expected prefixes.

# %% [markdown]
# ## What you learned
# You learned how AIDP lands multiple raw data formats into a governed Bronze layer without losing source traceability.
