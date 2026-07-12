# PARTICIPANT NOTEBOOK GUIDE
# Optional Streaming - Kafka-Compatible Wait-Time Events
#
# What this section does and why it matters:
# - Reads Kafka-compatible wait-time events, writes Bronze raw messages, parses Silver events, and aggregates one-minute Gold operational metrics.
# - Why it matters: This optional file demonstrates how live operational signals can complement batch context when a later workshop version reintroduces streaming.
#
# Inputs and outputs:
# - Inputs:
# - Kafka topic containing facility wait-time events
# - Outputs:
# - Bronze stream Delta
# - Silver stream Delta
# - Gold one-minute wait-time aggregate Delta
#
# Important parameters participants may change:
# - kafka_bootstrap_servers
# - kafka_topic
# - checkpoint_base
# - bronze_stream_path
# - silver_stream_path
# - gold_stream_path
#
# Plain-language explanation before the code:
# - Read the guide first, then run the code from top to bottom. The early code configures paths and helpers, the middle code builds or transforms data, and the final code writes outputs and prints validation evidence.
#
# Expected row counts or displayed results:
# - Streaming queries should start and write checkpointed Delta outputs as events arrive
#
# Safe rerun behaviour:
# - Use checkpoint folders for restart safety. Delete checkpoints only when deliberately replaying from scratch.
#
# Common errors and troubleshooting:
# - Kafka connection failure: confirm bootstrap server, topic, auth, and network rules.
# - Schema parse nulls: confirm event JSON contract.
#
# What you learned:
# - You learned where streaming signals fit into the same Bronze-Silver-Gold operating model.
# END PARTICIPANT NOTEBOOK GUIDE
# Optional Lab 5
# Stream analytics using Kafka-compatible facility wait-time events via AIDP.
#
# Source sample for local review:
#   data/streaming/wait_time_events.jsonl
#
# Target pattern:
#   Kafka topic -> AIDP Structured Streaming -> Bronze Delta -> Silver events
#   -> compact Gold operational aggregates for OAC.

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType, TimestampType


# -----------------------------------------------------------------------------
# 1. Configure Kafka, checkpoint, and Delta target paths.
# This optional pattern is retained for a future streaming version of the
# workshop; update these placeholders before running against a real topic.
# -----------------------------------------------------------------------------
kafka_bootstrap_servers = "<bootstrap-server>:9092"
kafka_topic = "mpha.facility.waittime.v1"
checkpoint_base = "oci://<bucket>@<namespace>/mpha/checkpoints/wait_time_stream"
bronze_stream_path = "oci://<bucket>@<namespace>/mpha/bronze_stream/facility_wait_time"
silver_stream_path = "oci://<bucket>@<namespace>/mpha/silver_stream/facility_wait_time"
gold_stream_path = "oci://<bucket>@<namespace>/mpha/gold_stream/wait_time_minute"


# -----------------------------------------------------------------------------
# 2. Define the event contract.
# Keeping the schema explicit makes malformed event handling easier to diagnose
# when participants test with Kafka-compatible streaming.
# -----------------------------------------------------------------------------
event_schema = StructType(
    [
        StructField("event_id", StringType(), False),
        StructField("event_time", TimestampType(), False),
        StructField("kafka_key", StringType(), True),
        StructField("topic", StringType(), True),
        StructField("facility_id", StringType(), False),
        StructField("district_id", StringType(), False),
        StructField("wait_minutes", IntegerType(), True),
        StructField("occupancy_rate", DoubleType(), True),
        StructField("queue_depth", IntegerType(), True),
        StructField("event_type", StringType(), True),
    ]
)


# -----------------------------------------------------------------------------
# 3. Read raw Kafka messages.
# The raw stream keeps key, value, topic, partition, offset, and timestamp for
# replay and troubleshooting.
# -----------------------------------------------------------------------------
raw_kafka = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
    .option("subscribe", kafka_topic)
    .option("startingOffsets", "latest")
    .load()
)

# -----------------------------------------------------------------------------
# 4. Bronze stream: persist raw message payloads.
# Bronze stores the raw JSON string plus Kafka lineage fields.
# -----------------------------------------------------------------------------
bronze_events = raw_kafka.select(
    F.col("key").cast("string").alias("message_key"),
    F.col("value").cast("string").alias("message_value"),
    F.col("topic"),
    F.col("partition"),
    F.col("offset"),
    F.col("timestamp").alias("kafka_timestamp"),
    F.current_timestamp().alias("_ingested_at"),
)

bronze_query = (
    bronze_events.writeStream.format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/bronze")
    .outputMode("append")
    .start(bronze_stream_path)
)

# -----------------------------------------------------------------------------
# 5. Silver stream: parse, type, clean, and classify pressure.
# This turns JSON payloads into typed wait-time events with operational pressure
# bands that can be queried directly.
# -----------------------------------------------------------------------------
silver_events = (
    bronze_events.select(F.from_json("message_value", event_schema).alias("event"), "_ingested_at")
    .select("event.*", "_ingested_at")
    .withColumn("wait_minutes", F.greatest(F.col("wait_minutes"), F.lit(0)))
    .withColumn("occupancy_rate", F.least(F.greatest(F.col("occupancy_rate"), F.lit(0.0)), F.lit(1.25)))
    .withColumn("queue_depth", F.greatest(F.col("queue_depth"), F.lit(0)))
    .withColumn(
        "pressure_band",
        F.when((F.col("wait_minutes") >= 75) | (F.col("occupancy_rate") >= 0.95), "High")
        .when((F.col("wait_minutes") >= 60) | (F.col("occupancy_rate") >= 0.85), "Medium")
        .otherwise("Watch"),
    )
)

silver_query = (
    silver_events.writeStream.format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/silver")
    .outputMode("append")
    .start(silver_stream_path)
)

# -----------------------------------------------------------------------------
# 6. Gold stream: one-minute operational aggregates.
# Watermarking allows late events while keeping the aggregate state bounded.
# -----------------------------------------------------------------------------
gold_minute = (
    silver_events.withWatermark("event_time", "15 minutes")
    .groupBy(F.window("event_time", "1 minute"), "facility_id", "district_id")
    .agg(
        F.round(F.avg("wait_minutes"), 1).alias("avg_wait_minutes"),
        F.max("wait_minutes").alias("max_wait_minutes"),
        F.round(F.avg("occupancy_rate"), 4).alias("avg_occupancy_rate"),
        F.max("queue_depth").alias("max_queue_depth"),
        F.count("*").alias("event_count"),
    )
    .withColumn("event_minute", F.col("window.start"))
    .withColumn(
        "pressure_band",
        F.when((F.col("max_wait_minutes") >= 75) | (F.col("avg_occupancy_rate") >= 0.95), "High")
        .when((F.col("max_wait_minutes") >= 60) | (F.col("avg_occupancy_rate") >= 0.85), "Medium")
        .otherwise("Watch"),
    )
    .drop("window")
)

# -----------------------------------------------------------------------------
# 7. Start the streaming queries.
# In a live workshop, monitor these query handles and stop them after validation.
# -----------------------------------------------------------------------------
gold_query = (
    gold_minute.writeStream.format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/gold")
    .outputMode("append")
    .start(gold_stream_path)
)
