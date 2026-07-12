# PARTICIPANT NOTEBOOK GUIDE
# 01 Bronze - Land MPHA Raw Signals
#
# What this section does and why it matters:
# - Loads the five CSV files, one JSONL event extract, and one GeoJSON document into Bronze Delta folders while preserving source fidelity and adding ingestion metadata.
# - Why it matters: Bronze is the audit and replay layer. It lets participants explain exactly which raw operational signals entered the workshop before any cleansing or business rules are applied.
#
# Inputs and outputs:
# - Inputs:
# - data/raw/*.csv copied to the Object Storage raw prefix
# - data/raw_json/facility_capacity_events.jsonl
# - data/raw_spatial/healthcare_service_areas.geojson
# - documents/MPHA_Winter_Respiratory_Response_Playbook.docx remains in the document landing area
# - Outputs:
# - 7 Bronze Delta folders under the configured bronze path
# - The playbook document remains available for the later RAG knowledge-base lab
#
# Important parameters participants may change:
# - raw_base, raw_json_base, raw_spatial_base, document_base, bronze_base
# - ingest_batch_id
#
# Plain-language explanation before the code:
# - Read the guide first, then run the code from top to bottom. The early code configures paths and helpers, the middle code builds or transforms data, and the final code writes outputs and prints validation evidence.
#
# Expected row counts or displayed results:
# - district profile: 5 rows
# - facility/provider master: 10 rows
# - facility operations daily: 1,810 rows
# - population health weekly: 780 rows
# - claims/membership/disbursement: 1,400 rows
# - facility capacity events: 80 rows
# - GeoJSON service areas: 25 features
#
# Safe rerun behaviour:
# - Safe for classroom reruns. The notebook overwrites Bronze Delta folders and preserves the current source snapshot with a fresh ingestion timestamp.
#
# Common errors and troubleshooting:
# - Path or authorization errors: verify bucket, namespace, policies, and external volume access.
# - Empty CSV outputs: confirm files were uploaded under mpha/raw and include headers.
# - JSON or GeoJSON parsing issues: confirm the JSONL and GeoJSON files were uploaded to the expected prefixes.
#
# What you learned:
# - You learned how AIDP lands multiple raw data formats into a governed Bronze layer without losing source traceability.
# END PARTICIPANT NOTEBOOK GUIDE
# Public Healthcare AIDP Workshop
# Bronze notebook: simplified raw sources -> Bronze Delta tables in AIDP.
#
# Update the bucket and namespace placeholders before running in Oracle AI Data Platform.

from pyspark.sql import functions as F


# -----------------------------------------------------------------------------
# 1. Configure landing-zone and Bronze-layer paths.
# Replace the bucket and namespace placeholders with the Object Storage location
# used by your workshop tenancy before running the notebook.
# -----------------------------------------------------------------------------
raw_base = "oci://<bucket>@<namespace>/mpha/raw"
raw_json_base = "oci://<bucket>@<namespace>/mpha/raw_json"
raw_spatial_base = "oci://<bucket>@<namespace>/mpha/raw_spatial"
document_base = "oci://<bucket>@<namespace>/mpha/documents"
bronze_base = "oci://<bucket>@<namespace>/mpha/bronze"
ingest_batch_id = "mpha_2025_h1_simplified_workshop"


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


# -----------------------------------------------------------------------------
# 5. Persist Bronze outputs.
# Downstream Silver notebooks read these Delta folders by table name.
# -----------------------------------------------------------------------------
for table_name, frame in bronze_tables.items():
    write_delta(frame, table_name)
    print(f"Wrote {table_name} to {bronze_base}/{table_name}")


# -----------------------------------------------------------------------------
# 6. Handoff checkpoint.
# The document is not converted to Delta here; it is consumed later by the
# document-vector / RAG knowledge-base flow.
# -----------------------------------------------------------------------------
print(
    "Bronze layer complete. The healthcare playbook document remains in the landing zone for the document-vector workflow:",
    f"{document_base}/MPHA_Winter_Respiratory_Response_Playbook.docx",
)
