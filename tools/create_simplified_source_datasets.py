from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "data/raw/district_health_profile.csv": ("CSV source", 5),
    "data/raw/facility_provider_master.csv": ("CSV source", 10),
    "data/raw/facility_operations_daily.csv": ("CSV source", 1810),
    "data/raw/population_health_weekly.csv": ("CSV source", 780),
    "data/raw/claims_membership_disbursement.csv": ("CSV source", 1400),
    "data/raw_json/facility_capacity_events.jsonl": ("JSONL source", 80),
    "data/raw_spatial/healthcare_service_areas.geojson": ("GeoJSON source", 25),
    "documents/MPHA_Winter_Respiratory_Response_Playbook.docx": ("DOCX source", None),
}


def count_csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader)
        return sum(1 for _ in reader)


def count_jsonl_rows(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def count_geojson_features(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return len(payload.get("features", []))


def actual_count(path: Path) -> int | None:
    if path.suffix == ".csv":
        return count_csv_rows(path)
    if path.suffix == ".jsonl":
        return count_jsonl_rows(path)
    if path.suffix == ".geojson":
        return count_geojson_features(path)
    return None


def main() -> None:
    failures = []
    for relative_path, (source_type, expected_rows) in EXPECTED_FILES.items():
        path = ROOT / relative_path
        if not path.exists():
            failures.append(f"Missing {source_type}: {relative_path}")
            continue
        rows = actual_count(path)
        if expected_rows is not None and rows != expected_rows:
            failures.append(
                f"{relative_path} has {rows} rows/features; expected {expected_rows}"
            )

    if failures:
        raise SystemExit("\n".join(failures))

    print("Validated simplified source set: 5 CSV, 1 JSONL, 1 GeoJSON, 1 DOCX.")


if __name__ == "__main__":
    main()
