# Oracle Analytics Cloud Dashboard Specification

## Dataset Connections

Connect OAC to Autonomous AI Lakehouse and expose the recommended dimensional Gold serving objects:

- `MPHA_DIM_DATE`
- `MPHA_DIM_DISTRICT`
- `MPHA_DIM_FACILITY`
- `MPHA_DIM_AGE_GROUP`
- `MPHA_DIM_QUALITY_EVENT`
- `MPHA_DIM_PRESSURE_BAND`
- `MPHA_DIM_DOCUMENT_CHUNK`
- `MPHA_DIM_COVERAGE_PROGRAM`
- `MPHA_DIM_CLAIM_TYPE`
- `MPHA_DIM_MEMBER_SEGMENT`
- `MPHA_DIM_ACCREDITATION_STATUS`
- `MPHA_FACT_FACILITY_ACCESS_DAILY`
- `MPHA_FACT_DISTRICT_PUBLIC_HEALTH_WEEKLY`
- `MPHA_FACT_IMMUNIZATION_EQUITY_WEEKLY`
- `MPHA_FACT_QUALITY_EVENT_SUMMARY`
- `MPHA_FACT_SPATIAL_ACCESS_INSIGHT`
- `MPHA_FACT_CAPACITY_EVENT`
- `MPHA_FACT_STREAM_WAIT_TIME_MINUTE`
- `MPHA_FACT_CLAIMS_MONTHLY`
- `MPHA_FACT_DISBURSEMENT_MONTHLY`
- `MPHA_FACT_MEMBERSHIP_SNAPSHOT`
- `MPHA_FACT_PROVIDER_ACCREDITATION`
- `MPHA_BRIDGE_CHAT_TOPIC_CHUNK`
- `MPHA_OAC_STAR_ACCESS_CAPACITY`
- `MPHA_OAC_STAR_PUBLIC_HEALTH_PRESSURE`
- `MPHA_OAC_STAR_IMMUNIZATION_EQUITY`
- `MPHA_OAC_STAR_QUALITY_EVENTS`
- `MPHA_OAC_STAR_SPATIAL_ACCESS`
- `MPHA_OAC_STAR_REALTIME_OPERATIONS`
- `MPHA_OAC_STAR_DOCUMENT_CHAT_CONTEXT`
- `MPHA_OAC_STAR_CLAIMS`
- `MPHA_OAC_STAR_DISBURSEMENTS`
- `MPHA_OAC_STAR_MEMBERSHIP`
- `MPHA_OAC_STAR_PROVIDER_ACCREDITATION`
- Optional: `MPHA_OAC_REALTIME_OPERATIONS`

## Recommended Joins

- `MPHA_FACT_FACILITY_ACCESS_DAILY.date_key` to `MPHA_DIM_DATE.date_key`
- `MPHA_FACT_FACILITY_ACCESS_DAILY.facility_key` to `MPHA_DIM_FACILITY.facility_key`
- `MPHA_FACT_FACILITY_ACCESS_DAILY.district_key` to `MPHA_DIM_DISTRICT.district_key`
- `MPHA_FACT_DISTRICT_PUBLIC_HEALTH_WEEKLY.district_key` to `MPHA_DIM_DISTRICT.district_key`
- `MPHA_FACT_IMMUNIZATION_EQUITY_WEEKLY.age_group_key` to `MPHA_DIM_AGE_GROUP.age_group_key`
- `MPHA_FACT_QUALITY_EVENT_SUMMARY.facility_key` to `MPHA_DIM_FACILITY.facility_key`
- `MPHA_FACT_QUALITY_EVENT_SUMMARY.district_key` to `MPHA_DIM_DISTRICT.district_key`
- `MPHA_FACT_QUALITY_EVENT_SUMMARY.quality_event_key` to `MPHA_DIM_QUALITY_EVENT.quality_event_key`
- `MPHA_FACT_SPATIAL_ACCESS_INSIGHT.pressure_band_key` to `MPHA_DIM_PRESSURE_BAND.pressure_band_key`
- `MPHA_FACT_CAPACITY_EVENT.facility_key` to `MPHA_DIM_FACILITY.facility_key`
- `MPHA_FACT_CAPACITY_EVENT.district_key` to `MPHA_DIM_DISTRICT.district_key`
- `MPHA_FACT_STREAM_WAIT_TIME_MINUTE.facility_key` to `MPHA_DIM_FACILITY.facility_key`
- `MPHA_FACT_STREAM_WAIT_TIME_MINUTE.district_key` to `MPHA_DIM_DISTRICT.district_key`
- `MPHA_BRIDGE_CHAT_TOPIC_CHUNK.document_chunk_key` to `MPHA_DIM_DOCUMENT_CHUNK.document_chunk_key`
- `MPHA_FACT_CLAIMS_MONTHLY.program_key` to `MPHA_DIM_COVERAGE_PROGRAM.program_key`
- `MPHA_FACT_CLAIMS_MONTHLY.claim_type_key` to `MPHA_DIM_CLAIM_TYPE.claim_type_key`
- `MPHA_FACT_DISBURSEMENT_MONTHLY.program_key` to `MPHA_DIM_COVERAGE_PROGRAM.program_key`
- `MPHA_FACT_MEMBERSHIP_SNAPSHOT.member_segment_key` to `MPHA_DIM_MEMBER_SEGMENT.member_segment_key`
- `MPHA_FACT_PROVIDER_ACCREDITATION.facility_key` to `MPHA_DIM_FACILITY.facility_key`
- `MPHA_FACT_PROVIDER_ACCREDITATION.district_key` to `MPHA_DIM_DISTRICT.district_key`
- `MPHA_FACT_PROVIDER_ACCREDITATION.accreditation_status_key` to `MPHA_DIM_ACCREDITATION_STATUS.accreditation_status_key`
- `MPHA_FACT_PROVIDER_ACCREDITATION.pressure_band_key` to `MPHA_DIM_PRESSURE_BAND.pressure_band_key`

For dashboard authors who prefer one dataset per canvas, use the `MPHA_OAC_STAR_*` views. For semantic-model authors, build joins directly from facts to dimensions.

## Canvas 1 - Executive Overview

Purpose: Give public-health leadership a quick view of operational pressure.

Wireframe style: Use the interactive OAC-style layout shown in `index.html#dashboards`: dark top bar, horizontal dashboard tabs, top filter strip, KPI row, chart panels, action table, spatial map view, and a right-side Assistant rail with the prompt bar anchored at the bottom.

Visuals:

- KPI: total outpatient visits
- KPI: average ED wait minutes
- KPI: facilities with high occupancy
- KPI: average public-health pressure index
- Map or district bar chart: pressure index by district
- Line chart: daily outpatient visits and emergency arrivals

## Canvas 2 - Access and Capacity

Purpose: Identify facilities with service-access risk.

Visuals:

- Bar chart: access risk score by facility
- Heatmap: facility by week with average occupancy
- Scatter plot: bed occupancy rate vs overtime hours
- Line chart: ED wait variance by facility
- Filter: facility type
- Filter: district

## Canvas 3 - Immunization Equity

Purpose: Monitor campaign performance by district and age group.

Visuals:

- Stacked bar: doses administered by age group
- Bar chart: completion rate by district
- Line chart: weekly doses administered
- Bar chart: immunization no-show rate by district
- Table: eligible population, booked appointments, missed appointments, doses administered

## Canvas 4 - Surveillance and Service Quality

Purpose: Connect respiratory pressure to operational and quality outcomes.

Visuals:

- Line chart: positivity rate and respiratory-related ED visits
- Bar chart: service-quality events by type
- Bar chart: service-quality events by severity
- KPI: average days to close events
- Table: high-severity events by facility

## Canvas 5 - Spatial Insights

Purpose: Use spatial data to identify where access constraints and public-health pressure point to mobile clinic or outreach actions.

Visuals:

- Map: district polygons shaded by pressure or residents per facility
- KPI: residents per facility
- KPI: highest pressure district
- Table: district, residents per facility, average distance, pressure, action
- Filter: district
- Filter: pressure band

## Canvas 6 - Chat with Data and Documents

Purpose: Demonstrate grounded analysis that combines structured Gold metrics with vectorized playbook content.

Visuals:

- Prompt input and suggested questions
- Retrieved playbook chunks with page and section
- Structured data context from Gold tables
- Generated answer panel with recommended action
- Filter: district
- Filter: facility type where the prompt relates to facility operations

## Canvas 7 - Real-Time Operations

Purpose: Demonstrate optional near-real-time and streaming analytics paths.

Visuals:

- KPI: high-pressure stream events
- KPI: average live wait minutes
- Table: latest capacity JSON events
- Status panel: GoldenGate CDC path
- Status panel: Kafka-compatible AIDP streaming path
- Filter: district
- Filter: pressure band

## Canvas 8 - Claims, Disbursement, Membership and Provider Accreditation

Purpose: Give payer and provider-operations teams a single view of claims, disbursement, membership, and accreditation risk.

Visuals:

- KPI: claims submitted
- KPI: claim denial rate
- KPI: total disbursed amount
- KPI: renewal-due members in next 60 days
- KPI: providers in high accreditation risk
- Bar chart: denial rate by coverage program and claim type
- Bar chart: disbursement amount by funding source
- Table: district, coverage program, members, renewals due, high-risk members
- Table: provider, accreditation status, score, corrective actions, days to expiry
- Filter: district
- Filter: pressure band

## Suggested Calculations

- `ED Wait Target Breach`: `avg_ed_wait_minutes > target_ed_wait_minutes`
- `Outpatient Wait Target Breach`: `avg_outpatient_wait_minutes > target_outpatient_wait_minutes`
- `High Occupancy`: `bed_occupancy_rate >= 0.90`
- `Immunization Gap`: `1 - completion_rate`
- `Quality Closure SLA Breach`: `days_to_close > 14`
- `Residents per Facility`: `population / facility_count`
- `Spatial Mobile Clinic Candidate`: `residents_per_facility >= 100000 OR public_health_pressure_index >= 45`
- `Streaming Pressure Band`: high when `max_wait_minutes >= 75 OR avg_occupancy_rate >= 0.95`
- `Claim Denial Rate`: `denied_claims / claims_submitted`
- `Payment Yield`: `total_paid_amount / total_submitted_amount`
- `Disbursement Exception Rate`: `(pending_disbursements + failed_disbursements) / disbursement_count`
- `Renewal Risk`: `renewal_due_60_days / member_count`
- `Provider Accreditation Risk`: high when accreditation is corrective action, score is below 82, or expiry is within 180 days

## Natural-Language Prompts

- "Which facilities need capacity intervention this week?"
- "Compare immunization completion rates across districts and age groups."
- "Summarize the operational impact of respiratory positivity increases."
- "Recommend three actions for districts with high public-health pressure."
- "Which districts should receive mobile clinic sessions this week?"
- "Use the MPHA playbook and Gold metrics to explain the action for high occupancy and ED waits."
- "What do the latest JSON capacity events imply for the Real-Time Operations dashboard?"
- "Which claim types have the highest denial rate by coverage program?"
- "Where are public-program disbursements pending or failing by funding source?"
- "Which districts have the highest member renewal risk?"
- "Which providers need accreditation corrective-action review first?"
