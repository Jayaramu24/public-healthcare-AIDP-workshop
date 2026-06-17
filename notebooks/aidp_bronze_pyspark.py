# Public Healthcare Lakehouse Analytics Workshop
# Bronze notebook: simplified raw sources -> Bronze Delta tables in AIDP.
#
# Update the bucket and namespace placeholders before running in Oracle AI Data Platform.

from pyspark.sql import functions as F


raw_base = "oci://<bucket>@<namespace>/mpha/raw"
raw_json_base = "oci://<bucket>@<namespace>/mpha/raw_json"
raw_spatial_base = "oci://<bucket>@<namespace>/mpha/raw_spatial"
document_base = "oci://<bucket>@<namespace>/mpha/documents"
bronze_base = "oci://<bucket>@<namespace>/mpha/bronze"
ingest_batch_id = "mpha_2025_h1_simplified_workshop"


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


def add_bronze_metadata(frame):
    return (
        frame.withColumn("_source_file", F.input_file_name())
        .withColumn("_ingest_batch_id", F.lit(ingest_batch_id))
        .withColumn("_ingested_at", F.current_timestamp())
    )


def write_delta(frame, name):
    frame.write.format("delta").mode("overwrite").save(f"{bronze_base}/{name}")


bronze_tables = {
    "bronze_district_health_profile": add_bronze_metadata(read_raw_csv("district_health_profile")),
    "bronze_facility_provider_master": add_bronze_metadata(read_raw_csv("facility_provider_master")),
    "bronze_facility_operations_daily": add_bronze_metadata(read_raw_csv("facility_operations_daily")),
    "bronze_population_health_weekly": add_bronze_metadata(read_raw_csv("population_health_weekly")),
    "bronze_claims_membership_disbursement": add_bronze_metadata(read_raw_csv("claims_membership_disbursement")),
    "bronze_facility_capacity_events": add_bronze_metadata(read_json_lines("facility_capacity_events")),
    "bronze_healthcare_service_areas_geojson": add_bronze_metadata(read_geojson_document("healthcare_service_areas")),
}


for table_name, frame in bronze_tables.items():
    write_delta(frame, table_name)
    print(f"Wrote {table_name} to {bronze_base}/{table_name}")


print(
    "Bronze layer complete. The healthcare playbook document remains in the landing zone for the document-vector workflow:",
    f"{document_base}/MPHA_Winter_Respiratory_Response_Playbook.docx",
)
