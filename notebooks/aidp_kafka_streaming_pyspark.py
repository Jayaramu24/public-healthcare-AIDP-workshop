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


kafka_bootstrap_servers = "<bootstrap-server>:9092"
kafka_topic = "mpha.facility.waittime.v1"
checkpoint_base = "oci://<bucket>@<namespace>/mpha/checkpoints/wait_time_stream"
bronze_stream_path = "oci://<bucket>@<namespace>/mpha/bronze_stream/facility_wait_time"
silver_stream_path = "oci://<bucket>@<namespace>/mpha/silver_stream/facility_wait_time"
gold_stream_path = "oci://<bucket>@<namespace>/mpha/gold_stream/wait_time_minute"


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


raw_kafka = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
    .option("subscribe", kafka_topic)
    .option("startingOffsets", "latest")
    .load()
)

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

gold_query = (
    gold_minute.writeStream.format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/gold")
    .outputMode("append")
    .start(gold_stream_path)
)

