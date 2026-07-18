from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


GUIDE_START = "# PARTICIPANT NOTEBOOK GUIDE"
GUIDE_END = "# END PARTICIPANT NOTEBOOK GUIDE"


def comment_block(lines: list[str]) -> str:
    out = [GUIDE_START]
    for line in lines:
        out.append(f"# {line}" if line else "#")
    out.append(GUIDE_END)
    out.append("")
    return "\n".join(out)


def strip_existing_guide(text: str) -> str:
    pattern = re.compile(
        rf"^# PARTICIPANT NOTEBOOK GUIDE\n.*?^# END PARTICIPANT NOTEBOOK GUIDE\n+",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub("", text)


def split_code_sections(code: str) -> list[tuple[str, str]]:
    lines = code.splitlines(keepends=True)
    starts: list[int] = []
    for idx, line in enumerate(lines):
        if re.match(r"# -{20,}\s*$", line):
            if idx + 1 < len(lines) and re.match(r"# \d+\.\s+", lines[idx + 1]):
                starts.append(idx)

    if not starts:
        return [("Notebook code", code)]

    sections: list[tuple[str, str]] = []
    if starts[0] > 0:
        sections.append(("Imports and setup", "".join(lines[: starts[0]]).rstrip() + "\n"))

    for pos, start in enumerate(starts):
        end = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
        chunk = "".join(lines[start:end]).rstrip() + "\n"
        title = "Code section"
        if start + 1 < len(lines):
            title = lines[start + 1].lstrip("#").strip().rstrip(".")
        sections.append((title, chunk))

    return [(title, chunk) for title, chunk in sections if chunk.strip()]


def md_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in text.strip().splitlines()]}


def code_cell(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.rstrip().splitlines()],
    }


NOTEBOOK_SPECS: dict[str, dict[str, object]] = {
    "aidp_bronze_pyspark.py": {
        "ipynb": "01_Bronze_Public_Healthcare.ipynb",
        "title": "01 Bronze - Land MPHA Raw Signals",
        "what": "Loads the five CSV files, one JSONL event extract, and one GeoJSON document into Bronze Delta folders while preserving source fidelity and adding ingestion metadata.",
        "why": "Bronze is the audit and replay layer. It lets participants explain exactly which raw operational signals entered the workshop before any cleansing or business rules are applied.",
        "inputs": [
            "Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/raw/*.csv",
            "Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/raw_json/facility_capacity_events.jsonl",
            "Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/raw_spatial/healthcare_service_areas.geojson",
            "Shared AIDP volume path /Volumes/e2eindustrydemos/default/e2eindustrydemovol/documents/MPHA_Winter_Respiratory_Response_Playbook.docx remains available for RAG",
        ],
        "outputs": [
            "7 Bronze Delta folders under `/Volumes/e2eindustrydemos/default/e2eindustrydemovol/workshop_runs/{participant_id}/bronze`",
            "The playbook document remains available for the later RAG knowledge-base lab",
        ],
        "parameters": [
            "volume_base",
            "participant_id",
            "raw_base, raw_json_base, raw_spatial_base, document_base, bronze_base",
            "ingest_batch_id",
        ],
        "expected": [
            "district profile: 5 rows",
            "facility/provider master: 10 rows",
            "facility operations daily: 1,810 rows",
            "population health weekly: 780 rows",
            "claims/membership/disbursement: 1,400 rows",
            "facility capacity events: 80 rows",
            "GeoJSON service areas: 25 features",
        ],
        "rerun": "Safe for classroom reruns. The notebook overwrites Bronze Delta folders and preserves the current source snapshot with a fresh ingestion timestamp.",
        "errors": [
            "Path or authorization errors: verify bucket, namespace, policies, and external volume access.",
            "Empty CSV outputs: confirm files were uploaded under mpha/raw and include headers.",
            "JSON or GeoJSON parsing issues: confirm the JSONL and GeoJSON files were uploaded to the expected prefixes.",
        ],
        "learned": "You learned how AIDP lands multiple raw data formats into a governed Bronze layer without losing source traceability.",
    },
    "aidp_silver_pyspark.py": {
        "ipynb": "02_Silver_Public_Healthcare.ipynb",
        "title": "02 Silver - Conform MPHA Operational Context",
        "what": "Reads Bronze Delta folders, types and cleans raw fields, standardizes entities, derives operational flags, and publishes reusable Silver Delta tables.",
        "why": "Silver is where MPHA decides whether the data can be trusted across claims, provider, facility, membership, public-health, JSON, and spatial use cases.",
        "inputs": ["Bronze Delta folders from the Bronze notebook"],
        "outputs": [
            "Silver district, facility/provider, facility-day, population-health, claims, accreditation, JSON capacity, spatial feature, and document-context tables under `/Volumes/e2eindustrydemos/default/e2eindustrydemovol/workshop_runs/{participant_id}/silver`",
        ],
        "parameters": ["volume_base", "participant_id", "bronze_base", "silver_base", "risk_reference_date"],
        "expected": [
            "Silver row counts should broadly match source grains: 5 districts, 10 facilities, 1,810 facility-days, 780 weekly population rows, and 1,400 claims rows",
            "Derived displays should show access risk, public-health pressure, denial rates, accreditation bands, JSON capacity fields, and spatial access context",
        ],
        "rerun": "Safe for repeat classroom runs. Silver outputs are overwritten from Bronze, so downstream notebooks should be rerun after a Silver rerun.",
        "errors": [
            "Missing Bronze table: rerun Bronze and verify bronze_base.",
            "Unexpected nulls after casts: inspect raw CSV values and confirm headers were not modified.",
            "Duplicate or ambiguous columns: keep the selected Silver joins and aliases unchanged.",
        ],
        "learned": "You learned how raw operational signals become trusted, typed, and reusable Silver data products.",
    },
    "aidp_gold_pyspark.py": {
        "ipynb": "03_Gold_Public_Healthcare.ipynb",
        "title": "03 Gold - Prepare Business-Ready Serving Outputs",
        "what": "Aggregates Silver data into Gold-stage outputs that support facility operations, public-health, claims, disbursement, membership, accreditation, JSON event, spatial, and document use cases.",
        "why": "Gold expresses the business decisions MPHA can make from trusted data, and it provides the staging layer for AI Lakehouse and analytics assets.",
        "inputs": ["Silver Delta folders from the Silver notebook"],
        "outputs": [
            "Gold-stage CSV folders under `/Volumes/e2eindustrydemos/default/e2eindustrydemovol/workshop_runs/{participant_id}/gold_stage` including claims summary, disbursement summary, membership summary, provider accreditation, facility access daily, spatial access insights, and executive overview",
        ],
        "parameters": ["volume_base", "participant_id", "silver_base", "gold_stage_base", "gold_snapshot_date"],
        "expected": [
            "gold_claims_summary: about 622 rows",
            "gold_facility_access_daily: 1,810 rows",
            "gold_immunization_equity_weekly: 780 rows",
            "gold_spatial_access_insights: 5 rows",
            "gold_executive_overview: 5 rows",
        ],
        "rerun": "Safe for reruns. Gold-stage CSV folders are overwritten, so consumers should refresh or reload after rerunning.",
        "errors": [
            "CSV datasource array/map errors: nested columns must be converted to JSON text before writing.",
            "Duplicate district columns: use the provided selected columns and avoid rejoining district attributes already present in Silver.",
            "Missing Silver table: rerun Silver and verify silver_base.",
        ],
        "learned": "You learned how business-ready Gold outputs are shaped from trusted Silver data for dashboards, ML, and AI Lakehouse publishing.",
    },
    "aidp_claims_star_ai_lakehouse_pyspark.py": {
        "ipynb": "04_Claims_Star_AI_Lakehouse_Load.ipynb",
        "title": "04 Claims Star Schema - Publish Gold to AI Lakehouse",
        "what": "Builds Date, District, Coverage Program, Claim Type dimensions and the monthly Claims fact, then inserts only new rows into the connected AI Lakehouse external catalog.",
        "why": "This is the governed business data product used by OAC, OAC Assistant, ML features, and the Claims SQL Agent.",
        "inputs": [
            "Participant Silver Delta folders under `/Volumes/e2eindustrydemos/default/e2eindustrydemovol/workshop_runs/{participant_id}/silver`",
            "Pre-created Claims star schema tables in the assigned AI Lakehouse schema, such as `goldailh.MPHA_P17`",
            "AIDP external catalog refresh completed so the participant schema is visible under `goldailh`",
        ],
        "outputs": [
            "mpha_dim_date",
            "mpha_dim_district",
            "mpha_dim_coverage_program",
            "mpha_dim_claim_type",
            "mpha_fact_claims_monthly",
        ],
        "parameters": ["volume_base", "participant_id", "silver_base", "target_catalog", "target_schema", "table_prefix", "write_mode"],
        "expected": [
            "mpha_fact_claims_monthly: about 622 rows on first successful load",
            "dimension row counts should be non-zero, and the validation SQL should return zero orphan rows",
        ],
        "rerun": "Designed for safe reruns. Existing natural keys are read from target tables and only new keys are inserted.",
        "errors": [
            "Target schema not found: refresh the `goldailh` external catalog in AIDP and confirm the assigned schema, for example `MPHA_P17`, is visible.",
            "Required table missing: run the Claims star schema DDL before this notebook.",
            "Executor memory failure: use the validated 1G driver/executor memory setting from the workshop troubleshooting notes.",
            "Table does not support truncate: do not truncate from Spark; use the idempotent append pattern.",
        ],
        "learned": "You learned how AIDP can publish a governed Claims star schema directly into AI Lakehouse while remaining safe for repeat execution.",
    },
    "aidp_claims_context_silver_pyspark.py": {
        "ipynb": "02B_Silver_Claims_Context_Extension.ipynb",
        "title": "02B Silver Extension - Add JSON and Spatial Context",
        "what": "Parses JSON facility capacity events, flattens GeoJSON service-area features, joins reference data, and creates a Silver operations/access context table.",
        "why": "This shows progressive enhancement: MPHA can add new operational signals after the original Claims dashboard is live without rebuilding the original Claims star schema.",
        "inputs": [
            "bronze_facility_capacity_events",
            "bronze_healthcare_service_areas_geojson",
            "bronze_facility_provider_master",
            "bronze_district_health_profile",
        ],
        "outputs": ["silver_operations_access_context"],
        "parameters": ["volume_base", "participant_id", "bronze_base", "silver_base"],
        "expected": [
            "The validation display should show 5 district-level records in the workshop sample",
            "Displayed fields include capacity_pressure_band, spatial_access_band, residents_per_facility, access_gap_score, and operations_access_risk_score",
        ],
        "rerun": "Safe for reruns. The Silver extension output is overwritten without changing the original Claims star schema flow.",
        "errors": [
            "Missing JSON/GeoJSON Bronze tables: rerun Bronze and confirm the additional raw formats were uploaded.",
            "Null spatial fields: inspect GeoJSON properties and district identifiers.",
            "Array-to-CSV issues do not apply here because this notebook writes Delta, not CSV.",
        ],
        "learned": "You learned how to extend an existing lakehouse product with JSON and spatial signals while keeping the original Claims flow stable.",
    },
    "aidp_claims_context_gold_ai_lakehouse_pyspark.py": {
        "ipynb": "03B_Gold_Claims_Context_AI_Lakehouse_Extension.ipynb",
        "title": "03B Gold Extension - Publish District Claims Context",
        "what": "Aggregates Silver operations/access context and claims metrics to district-month grain, writes Gold context, and optionally inserts new rows into AI Lakehouse.",
        "why": "This gives OAC and Assistant new district-level context for explaining why denial hotspots may align with capacity pressure or spatial access gaps.",
        "inputs": [
            "Participant Silver Delta folders under `/Volumes/e2eindustrydemos/default/e2eindustrydemovol/workshop_runs/{participant_id}/silver`",
            "silver_operations_access_context",
            "silver_claims_membership_disbursement",
            "mpha_fact_district_claims_context target table in the assigned AI Lakehouse schema",
        ],
        "outputs": [
            "gold_district_claims_context",
            "mpha_fact_district_claims_context",
            "mpha_claims_district_context_v",
        ],
        "parameters": ["volume_base", "participant_id", "silver_base", "gold_stage_base", "target_catalog", "target_schema", "table_prefix", "write_to_ai_lakehouse", "write_mode"],
        "expected": [
            "The workshop sample inserts about 5 district-month context rows",
            "Validation display should show priority score, denial rate, occupancy, wait pressure, and access gap fields",
        ],
        "rerun": "Designed for safe reruns. The notebook writes the Delta output and inserts only target keys that do not already exist.",
        "errors": [
            "Extension target table missing: run create_ai_lakehouse_claims_context_extension.sql first.",
            "Target schema not found: check target_catalog and target_schema.",
            "No new rows message: expected when rerunning after a successful insert.",
        ],
        "learned": "You learned how to add a new AI Lakehouse context table beside an existing star schema without disrupting the original dashboard.",
    },
    "aidp_ml_claims_denial_risk_pyspark.py": {
        "title": "05 ML - Train, Test, Evaluate, and Score Claims Denial Risk",
        "what": "Builds a claims denial risk feature frame, trains a Spark ML model, evaluates a held-out month, logs experiment metrics, and writes a scored review queue.",
        "why": "This turns trusted Gold data into a predictive action queue that claims operations can use before denial leakage grows.",
        "inputs": ["Gold-stage claims summary plus provider accreditation, capacity, and spatial context outputs"],
        "outputs": ["gold_claims_denial_risk_scores", "AIDP Experiment run metrics", "optional registered model artifact"],
        "parameters": ["volume_base", "participant_id", "gold_stage_base", "model_version", "experiment_name", "mlflow_run_name", "model_artifact_path", "enable_mlflow_tracking", "score_run_date"],
        "expected": [
            "Training uses January-April 2025; test uses May 2025; scoring uses June 2025",
            "Output review queue should include likely_denial_bucket and denial_risk_score",
            "Experiment metrics should include train/test counts, AUC values, and high-risk counts",
        ],
        "rerun": "Safe for repeat scoring. The output score folder is overwritten; MLflow runs create additional run history unless the run name is reused by the platform.",
        "errors": [
            "MLflow import unavailable: the notebook still runs but skips tracking and model logging.",
            "AUC cannot be computed: confirm the test period has both positive and negative labels.",
            "Missing Gold files: rerun the Gold-stage notebook and context extension if needed.",
        ],
        "learned": "You learned how to use the Gold layer for train/test/evaluate ML and publish a business-friendly review queue.",
    },
    "aidp_refinement_pyspark.py": {
        "title": "Legacy Refinement - Bronze to Curated Outputs",
        "what": "Refines earlier public healthcare sample data into curated outputs used by preview assets.",
        "why": "This file is kept for compatibility with earlier workshop assets and demonstrates the same raw-to-curated pattern.",
        "inputs": ["Earlier raw/curated sample files"],
        "outputs": ["Curated facility, district, and public-health preview outputs"],
        "parameters": ["Input and output paths at the top of the file"],
        "expected": ["Displayed previews should show facility, district, and pressure-index rows"],
        "rerun": "Safe when output folders can be overwritten in the local or AIDP environment.",
        "errors": ["Missing legacy source files: use the current Bronze/Silver/Gold notebooks for the main workshop path."],
        "learned": "You learned how the earlier refinement path relates to the current medallion flow.",
    },
    "aidp_kafka_streaming_pyspark.py": {
        "title": "Optional Streaming - Kafka-Compatible Wait-Time Events",
        "what": "Reads Kafka-compatible wait-time events, writes Bronze raw messages, parses Silver events, and aggregates one-minute Gold operational metrics.",
        "why": "This optional file demonstrates how live operational signals can complement batch context when a later workshop version reintroduces streaming.",
        "inputs": ["Kafka topic containing facility wait-time events"],
        "outputs": ["Bronze stream Delta", "Silver stream Delta", "Gold one-minute wait-time aggregate Delta"],
        "parameters": ["kafka_bootstrap_servers", "kafka_topic", "checkpoint_base", "bronze_stream_path", "silver_stream_path", "gold_stream_path"],
        "expected": ["Streaming queries should start and write checkpointed Delta outputs as events arrive"],
        "rerun": "Use checkpoint folders for restart safety. Delete checkpoints only when deliberately replaying from scratch.",
        "errors": ["Kafka connection failure: confirm bootstrap server, topic, auth, and network rules.", "Schema parse nulls: confirm event JSON contract."],
        "learned": "You learned where streaming signals fit into the same Bronze-Silver-Gold operating model.",
    },
}


def as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def guide_lines(spec: dict[str, object]) -> list[str]:
    lines = [
        str(spec["title"]),
        "",
        "What this section does and why it matters:",
        f"- {spec['what']}",
        f"- Why it matters: {spec['why']}",
        "",
        "Inputs and outputs:",
        "- Inputs:",
        *[f"- {item}" for item in as_list(spec["inputs"])],
        "- Outputs:",
        *[f"- {item}" for item in as_list(spec["outputs"])],
        "",
        "Important parameters participants may change:",
        *[f"- {item}" for item in as_list(spec["parameters"])],
        "",
        "Plain-language explanation before the code:",
        "- Read the guide first, then run the code from top to bottom. The early code configures paths and helpers, the middle code builds or transforms data, and the final code writes outputs and prints validation evidence.",
        "",
        "Expected row counts or displayed results:",
        *[f"- {item}" for item in as_list(spec["expected"])],
        "",
        "Safe rerun behaviour:",
        f"- {spec['rerun']}",
        "",
        "Common errors and troubleshooting:",
        *[f"- {item}" for item in as_list(spec["errors"])],
        "",
        "What you learned:",
        f"- {spec['learned']}",
    ]
    return lines


def markdown_overview(spec: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {spec['title']}",
            "",
            "## What this section does and why it matters",
            str(spec["what"]),
            "",
            f"**Why it matters:** {spec['why']}",
            "",
            "## Inputs and outputs",
            "",
            "**Inputs**",
            *[f"- {item}" for item in as_list(spec["inputs"])],
            "",
            "**Outputs**",
            *[f"- {item}" for item in as_list(spec["outputs"])],
            "",
            "## Important parameters participants may change",
            *[f"- `{item}`" if re.fullmatch(r"[A-Za-z0-9_, /.-]+", item) else f"- {item}" for item in as_list(spec["parameters"])],
        ]
    )


def markdown_execution_intro(spec: dict[str, object]) -> str:
    return "\n".join(
        [
            "## Plain-language explanation before the code",
            "Run the code cells from top to bottom. The early cells configure paths and helpers, the middle cells build or transform the data, and the final cells write outputs and display validation evidence.",
            "",
            "Keep the parameter values aligned with the Object Storage bucket, AIDP volume, external catalog, and schema prepared in Lab 0. If you change an input path, rerun the upstream notebook before rerunning this one.",
        ]
    )


def markdown_validation(spec: dict[str, object]) -> str:
    return "\n".join(
        [
            "## Expected row counts or displayed results",
            *[f"- {item}" for item in as_list(spec["expected"])],
            "",
            "## Safe rerun behaviour",
            str(spec["rerun"]),
            "",
            "## Common errors and troubleshooting",
            *[f"- {item}" for item in as_list(spec["errors"])],
        ]
    )


def markdown_learned(spec: dict[str, object]) -> str:
    return "\n".join(["## What you learned", str(spec["learned"])])


def section_markdown(title: str) -> str:
    clean = re.sub(r"^\d+\.\s*", "", title)
    return "\n".join(
        [
            f"## Code section - {clean}",
            "This code cell implements the step named above. Read the comments in the cell first, then run it and compare the output with the expected validation notes at the end of the notebook.",
        ]
    )


def update_py(path: Path, spec: dict[str, object]) -> None:
    original = strip_existing_guide(path.read_text())
    path.write_text(comment_block(guide_lines(spec)) + original, encoding="utf-8")


def update_ipynb(py_path: Path, ipynb_path: Path, spec: dict[str, object]) -> None:
    code = strip_existing_guide(py_path.read_text())
    cells = [md_cell(markdown_overview(spec)), md_cell(markdown_execution_intro(spec))]
    for title, chunk in split_code_sections(code):
        cells.append(md_cell(section_markdown(title)))
        cells.append(code_cell(chunk))
    cells.append(md_cell(markdown_validation(spec)))
    cells.append(md_cell(markdown_learned(spec)))

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "PySpark",
                "language": "python",
                "name": "pyspark",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    ipynb_path.write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for py_name, spec in NOTEBOOK_SPECS.items():
        py_path = NOTEBOOKS / py_name
        if not py_path.exists():
            raise FileNotFoundError(py_path)
        clean_code = strip_existing_guide(py_path.read_text())
        if "ipynb" in spec:
            update_ipynb(py_path, NOTEBOOKS / str(spec["ipynb"]), spec)
        py_path.write_text(comment_block(guide_lines(spec)) + clean_code, encoding="utf-8")
        print(f"Updated {py_path.name}")
        if "ipynb" in spec:
            print(f"Updated {spec['ipynb']}")


if __name__ == "__main__":
    main()
