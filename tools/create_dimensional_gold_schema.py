from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/gold_dimensional"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        if not rows:
            return
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def date_key(value: str) -> int:
    return int(value[:10].replace("-", ""))


def parse_date(value: str) -> datetime:
    return datetime.strptime(value[:10], "%Y-%m-%d")


def week_start(dt: datetime) -> str:
    return (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")


def pressure_band_key(value: float) -> int:
    if value >= 50:
        return 3
    if value >= 35:
        return 2
    return 1


def pressure_band_key_from_label(label: str) -> int:
    return {"Watch": 1, "Medium": 2, "High": 3}.get(label, 1)


def main() -> None:
    raw_facilities = read_csv(ROOT / "data/raw/facility_provider_master.csv")
    raw_community = read_csv(ROOT / "data/raw/district_health_profile.csv")
    facility_access = read_csv(ROOT / "data/gold/gold_facility_access_daily.csv")
    district_health = read_csv(ROOT / "data/gold/gold_district_public_health_weekly.csv")
    immunization = read_csv(ROOT / "data/gold/gold_immunization_equity_weekly.csv")
    quality = read_csv(ROOT / "data/gold/gold_quality_event_summary.csv")
    spatial = read_csv(ROOT / "data/gold/gold_spatial_access_insights.csv")
    capacity = read_csv(ROOT / "data/gold/gold_capacity_event_latest.csv")
    stream = read_csv(ROOT / "data/gold/gold_stream_wait_time_minute.csv")
    document_chunks = read_csv(ROOT / "data/gold/gold_document_chat_context.csv")
    claims_membership_disbursement = read_csv(ROOT / "data/raw/claims_membership_disbursement.csv")
    claims_summary = read_csv(ROOT / "data/gold/gold_claims_summary.csv")
    disbursement_summary = read_csv(ROOT / "data/gold/gold_disbursement_summary.csv")
    membership_summary = read_csv(ROOT / "data/gold/gold_membership_summary.csv")
    provider_accreditation_summary = read_csv(ROOT / "data/gold/gold_provider_accreditation_summary.csv")
    chat_examples = [
        {
            "question": "Which districts should receive mobile clinic sessions this week?",
            "structured_context": "Gold spatial access insights plus district pressure metrics",
            "retrieved_chunks": ["MPHA_PLAYBOOK_2025_CHUNK_004", "MPHA_PLAYBOOK_2025_CHUNK_006"],
            "sample_answer": "Prioritize districts where residents per facility and pressure are both high, then use the playbook's spatial response model to schedule mobile outreach.",
        },
        {
            "question": "What should we do when ED wait variance and occupancy rise together?",
            "structured_context": "Gold facility access daily metrics filtered by high pressure",
            "retrieved_chunks": ["MPHA_PLAYBOOK_2025_CHUNK_003", "MPHA_PLAYBOOK_2025_CHUNK_011"],
            "sample_answer": "Assign flex staffing, accelerate discharge coordination, and monitor diversion when ED wait variance and occupancy breach thresholds together.",
        },
        {
            "question": "How should respiratory positivity influence outreach?",
            "structured_context": "Gold district public health weekly metrics and capacity events",
            "retrieved_chunks": ["MPHA_PLAYBOOK_2025_CHUNK_005", "MPHA_PLAYBOOK_2025_CHUNK_008"],
            "sample_answer": "Rising positivity becomes urgent when paired with ED pressure, high no-show rates, or capacity alerts; extend respiratory sessions and targeted communications.",
        },
    ]

    dates = set()
    dates.update(row["service_date"] for row in facility_access)
    dates.update(row["week_start_date"] for row in district_health)
    dates.update(row["week_start_date"] for row in immunization)
    dates.update(row["event_timestamp"][:10] for row in capacity)
    dates.update(row["event_minute"][:10] for row in stream)
    dates.update(row["service_date"] for row in claims_membership_disbursement if row["service_date"])
    dates.update(row["claim_received_date"] for row in claims_membership_disbursement if row["claim_received_date"])
    dates.update(row["disbursement_date"] for row in claims_membership_disbursement if row["disbursement_date"])
    dates.update(row["enrollment_date"] for row in claims_membership_disbursement if row["enrollment_date"])
    dates.update(row["renewal_due_date"] for row in claims_membership_disbursement if row["renewal_due_date"])
    dates.update(row["last_survey_date"] for row in raw_facilities if row["last_survey_date"])
    dates.update(row["expiry_date"] for row in raw_facilities if row["expiry_date"])
    dates.update(row["service_month"] for row in claims_summary)
    dates.update(row["disbursement_month"] for row in disbursement_summary)
    dates.update(row["snapshot_date"] for row in membership_summary)
    dates.update(row["snapshot_date"] for row in provider_accreditation_summary)

    dim_date = []
    for value in sorted(dates):
        dt = parse_date(value)
        dim_date.append(
            {
                "date_key": date_key(value),
                "full_date": value,
                "calendar_year": dt.year,
                "calendar_quarter": (dt.month - 1) // 3 + 1,
                "month_number": dt.month,
                "month_name": dt.strftime("%B"),
                "week_start_date": week_start(dt),
                "day_of_week": dt.strftime("%A"),
                "is_week_start": "Y" if dt.weekday() == 0 else "N",
            }
        )

    district_key_by_id = {}
    dim_district = []
    for idx, row in enumerate(sorted(raw_community, key=lambda r: r["district_id"]), start=1):
        district_key_by_id[row["district_id"]] = idx
        dim_district.append(
            {
                "district_key": idx,
                "district_id": row["district_id"],
                "district_name": row["district_name"],
                "population": row["population"],
                "deprivation_index": row["deprivation_index"],
                "elderly_pct": row["elderly_pct"],
                "chronic_condition_pct": row["chronic_condition_pct"],
                "median_income_usd": row["median_income_usd"],
            }
        )

    facility_key_by_id = {}
    dim_facility = []
    for idx, row in enumerate(sorted(raw_facilities, key=lambda r: r["facility_id"]), start=1):
        facility_key_by_id[row["facility_id"]] = idx
        dim_facility.append(
            {
                "facility_key": idx,
                "facility_id": row["facility_id"],
                "facility_name": row["facility_name"],
                "facility_type": row["facility_type"],
                "district_key": district_key_by_id[row["district_id"]],
                "district_id": row["district_id"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "licensed_beds": row["licensed_beds"],
                "baseline_daily_visits": row["baseline_daily_visits"],
                "target_ed_wait_minutes": row["target_ed_wait_minutes"],
                "target_outpatient_wait_minutes": row["target_outpatient_wait_minutes"],
            }
        )

    age_sort = {"0-4": 1, "5-17": 2, "18-44": 3, "45-64": 4, "65-74": 5, "75+": 6}
    age_groups = sorted({row["age_group"] for row in immunization}, key=lambda label: age_sort.get(label, 999))
    age_key_by_label = {label: idx for idx, label in enumerate(age_groups, start=1)}
    dim_age_group = [
        {"age_group_key": key, "age_group": label, "sort_order": key}
        for label, key in age_key_by_label.items()
    ]

    quality_key_by_combo = {}
    dim_quality_event = []
    for row in sorted({(r["event_type"], r["severity"]) for r in quality}):
        idx = len(dim_quality_event) + 1
        quality_key_by_combo[row] = idx
        dim_quality_event.append(
            {"quality_event_key": idx, "event_type": row[0], "severity": row[1]}
        )

    dim_pressure_band = [
        {"pressure_band_key": 1, "pressure_band": "Watch", "lower_bound": 0, "upper_bound": 34.999, "description": "Routine monitoring"},
        {"pressure_band_key": 2, "pressure_band": "Medium", "lower_bound": 35, "upper_bound": 49.999, "description": "Operational watch list"},
        {"pressure_band_key": 3, "pressure_band": "High", "lower_bound": 50, "upper_bound": 100, "description": "Leadership action recommended"},
    ]

    document_key_by_chunk = {}
    dim_document_chunk = []
    for idx, row in enumerate(document_chunks, start=1):
        document_key_by_chunk[row["chunk_id"]] = idx
        dim_document_chunk.append(
            {
                "document_chunk_key": idx,
                "document_id": row["document_id"],
                "chunk_id": row["chunk_id"],
                "page_number": row["page_number"],
                "section_title": row["section_title"],
                "chunk_text": row["chunk_text"],
                "embedding_model": row["embedding_model"],
                "embedding_json": row["embedding_json"],
            }
        )

    program_key_by_code = {}
    dim_coverage_program = []
    program_combos = sorted(
        {
            (
                row["program_code"],
                row["coverage_program"],
                row["program_type"],
                row["funding_source"],
            )
            for row in claims_membership_disbursement
        }
    )
    for idx, row in enumerate(program_combos, start=1):
        program_key_by_code[row[0]] = idx
        dim_coverage_program.append(
            {
                "program_key": idx,
                "program_code": row[0],
                "coverage_program": row[1],
                "program_type": row[2],
                "funding_source": row[3],
            }
        )

    claim_type_key_by_combo = {}
    dim_claim_type = []
    claim_combos = sorted(
        {
            (row["claim_type"], row["service_category"], row["diagnosis_group"])
            for row in claims_membership_disbursement
        }
    )
    for idx, row in enumerate(claim_combos, start=1):
        claim_type_key_by_combo[row] = idx
        dim_claim_type.append(
            {
                "claim_type_key": idx,
                "claim_type": row[0],
                "service_category": row[1],
                "diagnosis_group": row[2],
            }
        )

    member_segment_key_by_combo = {}
    dim_member_segment = []
    member_segment_combos = sorted(
        {
            (row["age_group"], row["risk_segment"], row["chronic_condition_flag"])
            for row in claims_membership_disbursement
        }
    )
    for idx, row in enumerate(member_segment_combos, start=1):
        member_segment_key_by_combo[row] = idx
        dim_member_segment.append(
            {
                "member_segment_key": idx,
                "age_group": row[0],
                "risk_segment": row[1],
                "chronic_condition_flag": row[2],
            }
        )

    accreditation_status_key_by_combo = {}
    dim_accreditation_status = []
    accreditation_combos = sorted(
        {
            (
                row["accreditation_body"],
                row["accreditation_status"],
                row["accreditation_level"],
                row["specialty_scope"],
            )
            for row in raw_facilities
        }
    )
    for idx, row in enumerate(accreditation_combos, start=1):
        accreditation_status_key_by_combo[row] = idx
        dim_accreditation_status.append(
            {
                "accreditation_status_key": idx,
                "accreditation_body": row[0],
                "accreditation_status": row[1],
                "accreditation_level": row[2],
                "specialty_scope": row[3],
            }
        )

    fact_facility_access_daily = []
    for row in facility_access:
        fact_facility_access_daily.append(
            {
                "date_key": date_key(row["service_date"]),
                "facility_key": facility_key_by_id[row["facility_id"]],
                "pressure_band_key": pressure_band_key(float(row["access_risk_score"])),
                "outpatient_visits": row["outpatient_visits"],
                "emergency_arrivals": row["emergency_arrivals"],
                "admissions": row["admissions"],
                "discharges": row["discharges"],
                "avg_ed_wait_minutes": row["avg_ed_wait_minutes"],
                "avg_outpatient_wait_minutes": row["avg_outpatient_wait_minutes"],
                "ed_wait_variance_minutes": row["ed_wait_variance_minutes"],
                "outpatient_wait_variance_minutes": row["outpatient_wait_variance_minutes"],
                "bed_occupancy_rate": row["bed_occupancy_rate"],
                "high_occupancy_flag": row["high_occupancy_flag"],
                "staff_hours": row["staff_hours"],
                "overtime_hours": row["overtime_hours"],
                "patient_satisfaction_score": row["patient_satisfaction_score"],
                "access_risk_score": row["access_risk_score"],
            }
        )

    fact_district_public_health_weekly = []
    for row in district_health:
        fact_district_public_health_weekly.append(
            {
                "week_start_date_key": date_key(row["week_start_date"]),
                "district_key": district_key_by_id[row["district_id"]],
                "pressure_band_key": pressure_band_key(float(row["public_health_pressure_index"])),
                "eligible_population": row["eligible_population"],
                "appointments_booked": row["appointments_booked"],
                "missed_appointments": row["missed_appointments"],
                "doses_administered": row["doses_administered"],
                "completion_rate": row["completion_rate"],
                "immunization_no_show_rate": row["immunization_no_show_rate"],
                "tests_reported": row["tests_reported"],
                "positive_tests": row["positive_tests"],
                "positivity_rate": row["positivity_rate"],
                "respiratory_related_ed_visits": row["respiratory_related_ed_visits"],
                "public_health_pressure_index": row["public_health_pressure_index"],
            }
        )

    fact_immunization_equity_weekly = []
    for row in immunization:
        fact_immunization_equity_weekly.append(
            {
                "week_start_date_key": date_key(row["week_start_date"]),
                "district_key": district_key_by_id[row["district_id"]],
                "age_group_key": age_key_by_label[row["age_group"]],
                "eligible_population": row["eligible_population"],
                "appointments_booked": row["appointments_booked"],
                "missed_appointments": row["missed_appointments"],
                "walk_in_visits": row["walk_in_visits"],
                "doses_administered": row["doses_administered"],
                "completion_rate": row["completion_rate"],
                "immunization_no_show_rate": row["immunization_no_show_rate"],
            }
        )

    fact_quality_event_summary = []
    for row in quality:
        fact_quality_event_summary.append(
            {
                "facility_key": facility_key_by_id[row["facility_id"]],
                "quality_event_key": quality_key_by_combo[(row["event_type"], row["severity"])],
                "event_count": row["event_count"],
                "avg_days_to_close": row["avg_days_to_close"],
                "sla_breach_events": row["sla_breach_events"],
                "avoidable_readmission_events": row["avoidable_readmission_events"],
            }
        )

    fact_spatial_access_insight = []
    for row in spatial:
        fact_spatial_access_insight.append(
            {
                "district_key": district_key_by_id[row["district_id"]],
                "pressure_band_key": pressure_band_key(float(row["public_health_pressure_index"])),
                "facility_count": row["facility_count"],
                "residents_per_facility": row["residents_per_facility"],
                "avg_distance_to_facility_km": row["avg_distance_to_facility_km"],
                "public_health_pressure_index": row["public_health_pressure_index"],
                "high_pressure_facilities": row["high_pressure_facilities"],
                "spatial_business_insight": row["spatial_business_insight"],
            }
        )

    fact_capacity_event = []
    for row in capacity:
        fact_capacity_event.append(
            {
                "event_date_key": date_key(row["event_timestamp"]),
                "event_timestamp": row["event_timestamp"],
                "facility_key": facility_key_by_id[row["facility_id"]],
                "pressure_band_key": pressure_band_key_from_label(row["capacity_pressure_band"]),
                "current_occupancy_rate": row["current_occupancy_rate"],
                "waiting_room_count": row["waiting_room_count"],
                "avg_ed_wait_minutes": row["avg_ed_wait_minutes"],
                "triage_total": row["triage_total"],
                "supply_alert_count": row["supply_alert_count"],
                "ambulance_diversion_status": row["ambulance_diversion_status"],
            }
        )

    fact_stream_wait_time_minute = []
    for row in stream:
        fact_stream_wait_time_minute.append(
            {
                "event_date_key": date_key(row["event_minute"]),
                "event_minute": row["event_minute"],
                "facility_key": facility_key_by_id[row["facility_id"]],
                "pressure_band_key": pressure_band_key_from_label(row["pressure_band"]),
                "avg_wait_minutes": row["avg_wait_minutes"],
                "max_wait_minutes": row["max_wait_minutes"],
                "avg_occupancy_rate": row["avg_occupancy_rate"],
                "max_queue_depth": row["max_queue_depth"],
                "event_count": row["event_count"],
            }
        )

    bridge_chat_topic_chunk = []
    for example in chat_examples:
        for rank, chunk_id in enumerate(example["retrieved_chunks"], start=1):
            bridge_chat_topic_chunk.append(
                {
                    "chat_topic_key": len(bridge_chat_topic_chunk) + 1,
                    "question": example["question"],
                    "structured_context": example["structured_context"],
                    "document_chunk_key": document_key_by_chunk[chunk_id],
                    "relevance_rank": rank,
                    "sample_answer": example["sample_answer"],
                }
            )

    fact_claims_monthly = []
    for row in claims_summary:
        fact_claims_monthly.append(
            {
                "service_month_date_key": date_key(row["service_month"]),
                "district_key": district_key_by_id[row["district_id"]],
                "program_key": program_key_by_code[row["program_code"]],
                "claim_type_key": claim_type_key_by_combo[(row["claim_type"], row["service_category"], row["diagnosis_group"])],
                "claims_submitted": row["claims_submitted"],
                "approved_claims": row["approved_claims"],
                "denied_claims": row["denied_claims"],
                "pending_claims": row["pending_claims"],
                "total_submitted_amount": row["total_submitted_amount"],
                "total_approved_amount": row["total_approved_amount"],
                "total_paid_amount": row["total_paid_amount"],
                "avg_processing_days": row["avg_processing_days"],
                "denial_rate": row["denial_rate"],
            }
        )

    fact_disbursement_monthly = []
    for row in disbursement_summary:
        fact_disbursement_monthly.append(
            {
                "disbursement_month_date_key": date_key(row["disbursement_month"]),
                "district_key": district_key_by_id[row["district_id"]],
                "program_key": program_key_by_code[row["program_code"]],
                "payee_type": row["payee_type"],
                "disbursement_count": row["disbursement_count"],
                "paid_disbursements": row["paid_disbursements"],
                "pending_disbursements": row["pending_disbursements"],
                "failed_disbursements": row["failed_disbursements"],
                "total_disbursement_amount": row["total_disbursement_amount"],
                "avg_payment_cycle_days": row["avg_payment_cycle_days"],
            }
        )

    fact_membership_snapshot = []
    for row in membership_summary:
        fact_membership_snapshot.append(
            {
                "snapshot_date_key": date_key(row["snapshot_date"]),
                "district_key": district_key_by_id[row["district_id"]],
                "program_key": program_key_by_code[row["program_code"]],
                "member_segment_key": member_segment_key_by_combo[
                    (row["age_group"], row["risk_segment"], row["chronic_condition_flag"])
                ],
                "member_count": row["member_count"],
                "active_members": row["active_members"],
                "renewal_due_members": row["renewal_due_members"],
                "suspended_members": row["suspended_members"],
                "renewal_due_60_days": row["renewal_due_60_days"],
                "high_risk_members": row["high_risk_members"],
            }
        )

    fact_provider_accreditation = []
    for row in provider_accreditation_summary:
        fact_provider_accreditation.append(
            {
                "snapshot_date_key": date_key(row["snapshot_date"]),
                "last_survey_date_key": date_key(row["last_survey_date"]),
                "expiry_date_key": date_key(row["expiry_date"]),
                "facility_key": facility_key_by_id[row["facility_id"]],
                "accreditation_status_key": accreditation_status_key_by_combo[
                    (
                        row["accreditation_body"],
                        row["accreditation_status"],
                        row["accreditation_level"],
                        row["specialty_scope"],
                    )
                ],
                "pressure_band_key": pressure_band_key_from_label(row["accreditation_risk_band"]),
                "provider_id": row["provider_id"],
                "accreditation_score": row["accreditation_score"],
                "corrective_action_count": row["corrective_action_count"],
                "days_to_expiry": row["days_to_expiry"],
            }
        )

    write_csv("dim_date.csv", dim_date)
    write_csv("dim_district.csv", dim_district)
    write_csv("dim_facility.csv", dim_facility)
    write_csv("dim_age_group.csv", dim_age_group)
    write_csv("dim_quality_event.csv", dim_quality_event)
    write_csv("dim_pressure_band.csv", dim_pressure_band)
    write_csv("dim_document_chunk.csv", dim_document_chunk)
    write_csv("dim_coverage_program.csv", dim_coverage_program)
    write_csv("dim_claim_type.csv", dim_claim_type)
    write_csv("dim_member_segment.csv", dim_member_segment)
    write_csv("dim_accreditation_status.csv", dim_accreditation_status)
    write_csv("fact_facility_access_daily.csv", fact_facility_access_daily)
    write_csv("fact_district_public_health_weekly.csv", fact_district_public_health_weekly)
    write_csv("fact_immunization_equity_weekly.csv", fact_immunization_equity_weekly)
    write_csv("fact_quality_event_summary.csv", fact_quality_event_summary)
    write_csv("fact_spatial_access_insight.csv", fact_spatial_access_insight)
    write_csv("fact_capacity_event.csv", fact_capacity_event)
    write_csv("fact_stream_wait_time_minute.csv", fact_stream_wait_time_minute)
    write_csv("bridge_chat_topic_chunk.csv", bridge_chat_topic_chunk)
    write_csv("fact_claims_monthly.csv", fact_claims_monthly)
    write_csv("fact_disbursement_monthly.csv", fact_disbursement_monthly)
    write_csv("fact_membership_snapshot.csv", fact_membership_snapshot)
    write_csv("fact_provider_accreditation.csv", fact_provider_accreditation)


if __name__ == "__main__":
    main()
