-- Optional real-time and streaming Gold serving objects.
--
-- Use this file with Optional Lab 4 (OCI GoldenGate) and Optional Lab 5
-- (Kafka-compatible streaming through AIDP).

CREATE TABLE mpha_rt_appointment_change (
  change_ts TIMESTAMP,
  operation_type VARCHAR2(20),
  appointment_id VARCHAR2(40),
  facility_id VARCHAR2(10),
  district_id VARCHAR2(10),
  appointment_status VARCHAR2(40),
  service_line VARCHAR2(80),
  scheduled_start_ts TIMESTAMP,
  updated_by_system VARCHAR2(80)
);

CREATE TABLE mpha_stream_wait_time_gold (
  event_minute TIMESTAMP,
  facility_id VARCHAR2(10),
  district_id VARCHAR2(10),
  avg_wait_minutes NUMBER,
  max_wait_minutes NUMBER,
  avg_occupancy_rate NUMBER,
  max_queue_depth NUMBER,
  event_count NUMBER,
  pressure_band VARCHAR2(20)
);

CREATE OR REPLACE VIEW mpha_oac_realtime_operations AS
SELECT
  s.event_minute,
  s.facility_id,
  f.facility_name,
  s.district_id,
  f.district_name,
  s.avg_wait_minutes,
  s.max_wait_minutes,
  s.avg_occupancy_rate,
  s.max_queue_depth,
  s.event_count,
  s.pressure_band
FROM mpha_stream_wait_time_gold s
LEFT JOIN (
  SELECT DISTINCT facility_id, facility_name, district_id, district_name
  FROM mpha_gold_facility_access_daily
) f
  ON s.facility_id = f.facility_id;

