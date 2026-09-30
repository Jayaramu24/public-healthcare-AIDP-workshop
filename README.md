# Public Healthcare AIDP Workshop

[Open the published workshop](https://jayaramu24.github.io/public-healthcare-AIDP-workshop/)

A synthetic Metro Public Health Authority workshop using Object Storage, Oracle
AI Data Platform, Autonomous AI Lakehouse and AI Powered Business Analytics (OAC).

## Workshop sequence

All labs are required. Administrators prepare Lab 0; participants follow:

1. Bronze, Silver and Gold staging
2. Claims star schema in AI Lakehouse
3. JSON and spatial context extension
4. ML training, held-out evaluation, scoring and model registration
5. The Lab 4A five-task workflow exercise
6. RAG knowledge base and Claims copilot (Labs 5 and 6)
7. Facility Access Daily design challenge
8. AI Powered Business Analytics

Deployment names in screenshots are illustrative. Use the administrator-assigned
workspace, participant folder, raw/output volumes, catalogs, schema and compute.

## Downloads

- [Screenshot-based PDF guide](workshop_guide.pdf)
- [Execution pack: notebooks, SQL and handoff instructions](downloads/mpha_workshop_execution_pack.zip)
- [Eight notebooks](downloads/mpha_notebooks_only.zip)
- [SQL scripts](downloads/mpha_sql_scripts_only.zip)
- [Raw data: five CSV, one JSONL, one GeoJSON, one DOCX](downloads/public_healthcare_raw_data_bundle.zip)
- [Offline PDF and execution bundle](downloads/offline_review_bundle.zip)
- [Configuration checklist](participant_configuration.md)
- [Read first](README_FIRST.md)
- [Validation scope and remaining checks](VALIDATION_NOTES.md)
- [On-demand inspection notebook](notebooks/99_On_Demand_Validation_Commands.ipynb)

Use preloaded notebooks first. Download and extract the ZIP to restore missing
files; GitHub's individual file links open a preview, not an AIDP import.
Notebook file numbers are stable names and need not match lab numbers.

## Publishing

GitHub Pages publishes the main branch repository root. Push an approved commit
to main, wait for the Pages deployment to finish, then refresh the same site URL.
Never commit credentials, wallets, private participant mappings or session tokens.
