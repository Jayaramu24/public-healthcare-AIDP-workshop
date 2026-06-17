# Optional Lab 4 - Real-Time Analytics with OCI GoldenGate

## Goal

Add a near-real-time operational analytics path for MPHA by using OCI GoldenGate to capture changes from source operational tables and publish them into the lakehouse serving flow.

## Business Scenario

MPHA wants operations leaders to see appointment changes, admission updates, discharge status, and quality-event closure changes without waiting for the next scheduled batch load. This lab adds a real-time pattern beside the main medallion batch flow.

## Reference Architecture

1. Operational source database emits changes for appointments, admissions, discharges, and quality events.
2. OCI GoldenGate captures inserts, updates, and deletes from the source.
3. OCI GoldenGate delivers change events to a target such as OCI Streaming, Object Storage, or Autonomous AI Lakehouse staging tables.
4. AIDP or AI Lakehouse compacts the changes into real-time Gold serving tables.
5. OAC reads the real-time Gold view for the Real-Time Operations dashboard tab.

## Suggested Source Tables

| Source table | Example change | Business value |
| --- | --- | --- |
| `appointment` | Appointment booked, cancelled, no-show, completed | Live access and demand changes. |
| `encounter` | ED arrival, admission, discharge | Live patient-flow pressure signal. |
| `bed_status` | Occupied, available, blocked | Capacity and diversion monitoring. |
| `quality_event` | Event created, severity changed, closed | Quality action queue freshness. |

## Setup Tasks

1. Create or identify a non-production source schema with synthetic operational tables.
2. Create the GoldenGate deployment and assign network connectivity.
3. Configure the extract process for the source tables.
4. Configure the distribution path to the target.
5. Configure the replicat or handler for the target staging table or topic.
6. Run `sql/realtime_gold_tables.sql` in AI Lakehouse to create the optional Gold structures.
7. Connect the OAC Real-Time Operations tab to `MPHA_OAC_REALTIME_OPERATIONS`.

## Validation

- Insert a synthetic appointment status change.
- Confirm GoldenGate captures the change.
- Confirm the target stream or table receives the change.
- Confirm the real-time Gold object updates.
- Confirm the OAC Real-Time Operations tab reflects the change after refresh.

## Facilitator Notes

- Keep this lab optional because GoldenGate setup depends on source connectivity and tenancy policy.
- Use only synthetic operational tables during workshop delivery.
- Position this pattern as change-data capture for transactional systems, not as the primary path for high-volume telemetry.

