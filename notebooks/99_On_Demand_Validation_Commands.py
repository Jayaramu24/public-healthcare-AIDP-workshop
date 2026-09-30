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
# PARTICIPANT NOTEBOOK GUIDE
# 99 On-Demand Validation Commands
#
# What this section does and why it matters:
# - Gives participants a few simple commands to inspect data written by the
#   Bronze, Silver, Gold, context-extension, and AI Lakehouse load notebooks.
# - Why it matters: Participants can verify data movement only when they need to,
#   without adding extra validation logic to every workshop notebook.
#
# Inputs and outputs:
# - Inputs:
# - Mounted Object Storage paths under your assigned output_base
# - Optional AI Lakehouse external catalog tables under the assigned schema
# - Outputs:
# - Sample rows, row counts, and distinct values displayed in the notebook
#
# Important parameters participants may change:
# - volume_base
# - participant_id
# - target_catalog
# - target_schema
# - layer_base
# - object_name
# - file_format
# - table_name
# - column_name
#
# Safe rerun behaviour:
# - Safe to rerun. These commands only read data and display results.
#
# Common errors and troubleshooting:
# - Path not found: confirm the upstream notebook finished and participant_id is correct.
# - Table not found: confirm the AI Lakehouse schema was created, loaded, and refreshed in the AIDP external catalog.
# - Column not found: run the sample command first and copy the exact column name from the output.
#
# What you learned:
# - You learned how to validate row samples, row counts, and business values from
#   each layer without changing the medallion pipeline.
# END PARTICIPANT NOTEBOOK GUIDE

# %%
# -----------------------------------------------------------------------------
# 1. Configure once.
# Change only the participant and schema values assigned to you.


# %%
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

target_catalog = "REPLACE_WITH_YOUR_AILH_CATALOG"
target_schema = "REPLACE_WITH_YOUR_AILH_SCHEMA"  # Assigned schema; not a screenshot example.

if participant_id == "REPLACE_WITH_YOUR_PARTICIPANT_ID":
    raise ValueError("Set participant_id to your AIDP participant folder name before running validation commands.")

bronze_base = f"{output_base}/bronze"
silver_base = f"{output_base}/silver"
gold_stage_base = f"{output_base}/gold_stage"

if "REPLACE_" in target_catalog or "REPLACE_" in target_schema:
    raise ValueError("Set your assigned external catalog and schema before continuing.")


# %%
# -----------------------------------------------------------------------------
# 2. Small read-only helpers.
# These helpers do not write or change data. They only read from a path or table.
# Use file_format="delta" for Bronze/Silver Delta folders.
# Use file_format="csv" for Gold-stage CSV folders from the core Gold notebook.


# %%
# -----------------------------------------------------------------------------
def load_from_path(layer_base, object_name, file_format="delta"):
    path = f"{layer_base}/{object_name}"
    if file_format.lower() == "csv":
        return spark.read.option("header", "true").option("inferSchema", "true").csv(path)
    return spark.read.format(file_format).load(path)


def show_path_sample(layer_base, object_name, file_format="delta", rows=10):
    df = load_from_path(layer_base, object_name, file_format)
    print(f"Sample rows from: {layer_base}/{object_name}")
    df.limit(rows).show(truncate=False)


def show_path_count(layer_base, object_name, file_format="delta"):
    df = load_from_path(layer_base, object_name, file_format)
    row_count = df.count()
    print(f"Row count for {layer_base}/{object_name}: {row_count}")


def show_path_distinct_values(layer_base, object_name, column_name, file_format="delta", rows=100):
    df = load_from_path(layer_base, object_name, file_format)
    print(f"Distinct values for {column_name} in {layer_base}/{object_name}")
    df.select(column_name).distinct().orderBy(column_name).show(rows, truncate=False)


def show_table_sample(table_name, rows=10):
    print(f"Sample rows from table: {table_name}")
    spark.table(table_name).limit(rows).show(truncate=False)


def show_table_count(table_name):
    row_count = spark.table(table_name).count()
    print(f"Row count for {table_name}: {row_count}")


def show_table_distinct_values(table_name, column_name, rows=100):
    print(f"Distinct values for {column_name} in {table_name}")
    spark.table(table_name).select(column_name).distinct().orderBy(column_name).show(rows, truncate=False)


# %%
# -----------------------------------------------------------------------------
# 3. Command: fetch sample rows for all columns from an Object Storage layer.
# Change layer_base, object_name, file_format, and rows as needed.


# %%
# -----------------------------------------------------------------------------
show_path_sample(
    layer_base=silver_base,
    object_name="silver_claims_membership_disbursement",
    file_format="delta",
    rows=10,
)


# %%
# -----------------------------------------------------------------------------
# 4. Command: find how many records were written to an Object Storage layer.
# For overwrite notebooks, this count is the number of rows available after the
# write completed.


# %%
# -----------------------------------------------------------------------------
show_path_count(
    layer_base=silver_base,
    object_name="silver_claims_membership_disbursement",
    file_format="delta",
)


# %%
# -----------------------------------------------------------------------------
# 5. Command: list unique or distinct values for a given column.
# Run the sample command first if you need to confirm the exact column name.


# %%
# -----------------------------------------------------------------------------
show_path_distinct_values(
    layer_base=silver_base,
    object_name="silver_claims_membership_disbursement",
    column_name="claim_status",
    file_format="delta",
    rows=100,
)


# %%
# -----------------------------------------------------------------------------
# 6. Command: validate a Gold-stage CSV output.
# The core Gold notebook writes CSV folders, so set file_format to csv.


# %%
# -----------------------------------------------------------------------------
show_path_sample(
    layer_base=gold_stage_base,
    object_name="gold_claims_summary",
    file_format="csv",
    rows=10,
)

show_path_count(
    layer_base=gold_stage_base,
    object_name="gold_claims_summary",
    file_format="csv",
)


# %%
# -----------------------------------------------------------------------------
# 7. Command: validate an AI Lakehouse table after the load notebook.
# Use your assigned target_schema, from your configuration sheet.


# %%
# -----------------------------------------------------------------------------
if target_schema != "REPLACE_WITH_YOUR_AILH_SCHEMA":
    claims_fact_table = f"{target_catalog}.{target_schema}.mpha_fact_claims_monthly"
    claim_type_table = f"{target_catalog}.{target_schema}.mpha_dim_claim_type"

    show_table_sample(claims_fact_table, rows=10)
    show_table_count(claims_fact_table)
    show_table_distinct_values(claim_type_table, "service_category", rows=100)
else:
    print("Set target_schema before running the AI Lakehouse table validation commands.")


# %%
# -----------------------------------------------------------------------------
# 8. Optional: capture exact inserted rows for an AI Lakehouse table.
# Run the first line before your load notebook, then run the last two lines after
# your load notebook. This is only needed when you want before/after evidence.


# %%
# -----------------------------------------------------------------------------
# before_count = spark.table(claims_fact_table).count()
# after_count = spark.table(claims_fact_table).count()
# print(f"Rows inserted by the load notebook: {after_count - before_count}")
