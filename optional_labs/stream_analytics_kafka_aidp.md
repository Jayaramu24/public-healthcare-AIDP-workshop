# Optional Lab 5 - Stream Analytics with Kafka-Compatible Streaming via AIDP

## Goal

Process facility wait-time telemetry as a Kafka-compatible stream, refine it in AIDP with Structured Streaming, and publish compact Gold metrics for the OAC Real-Time Operations dashboard.

## Business Scenario

Facility command centers emit wait-time, occupancy, queue-depth, and triage snapshots throughout the day. MPHA wants a streaming analytics path that can highlight rising pressure before the daily batch closes.

## Provided Sample Data

- `data/streaming/wait_time_events.jsonl`
- `notebooks/aidp_kafka_streaming_pyspark.py`
- `sql/realtime_gold_tables.sql`

## Stream Event Shape

| Field | Description |
| --- | --- |
| `event_id` | Unique event identifier. |
| `event_time` | Event timestamp from the source system. |
| `facility_id`, `district_id` | Facility and district keys. |
| `wait_minutes` | Current average wait-time signal. |
| `occupancy_rate` | Current occupancy signal. |
| `queue_depth` | Current waiting queue depth. |
| `event_type` | Event classification. |

## AIDP Medallion Logic

| Layer | Object | Logic |
| --- | --- | --- |
| Bronze | `bronze_stream/facility_wait_time` | Preserve Kafka key, value, topic, partition, offset, timestamp, and ingestion timestamp. |
| Silver | `silver_stream/facility_wait_time` | Parse JSON, type fields, clamp rates, reject negative counts, and derive pressure band. |
| Gold | `gold_stream/wait_time_minute` | Aggregate by one-minute window, facility, and district; calculate average wait, max wait, average occupancy, queue depth, event count, and pressure band. |

## Setup Tasks

1. Create or identify a Kafka-compatible stream topic named `mpha.facility.waittime.v1`.
2. Publish the sample JSONL events to the topic, or configure a simulator that emits equivalent messages.
3. Open `notebooks/aidp_kafka_streaming_pyspark.py` in AIDP.
4. Set the Kafka bootstrap server, checkpoint paths, and Delta output paths.
5. Run the streaming notebook.
6. Use `sql/realtime_gold_tables.sql` to create AI Lakehouse real-time serving objects.
7. Point the OAC Real-Time Operations tab to `MPHA_OAC_REALTIME_OPERATIONS`.

## Validation

- Confirm Bronze Delta contains raw Kafka messages.
- Confirm Silver Delta contains parsed wait-time events.
- Confirm Gold stream aggregates update by minute.
- Filter the OAC Real-Time Operations dashboard by district and pressure band.

## Facilitator Notes

- Use this lab to explain how AIDP supports a continuous medallion pattern.
- Keep stream aggregates small and purpose-built for operational decisions.
- For a short workshop, pre-stage the topic and simulator before participants begin.

