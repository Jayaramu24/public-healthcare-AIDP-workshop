# MPHA Oracle Analytics AI workshop

A LiveLabs-style, screenshot-backed three-hour workshop for 15–20 experienced analysts over Zoom. Use the existing synthetic MPHA claims data already in OAC. The screenshots were captured from the actual tenant; generated AI suggestions and errors are identified honestly.

**Start with [the HTML runbook](index.html)** for navigation, copyable prompts, and full-resolution images. GitHub readers can use the individual Markdown labs below.

**Delivery format:** seven feature labs remain hands-on in the original workshop OAC environment; Semantic Modeler is a verified 15-minute instructor demo in Industry Analytics. Seven AI capabilities have now been exercised successfully. Lab 9 adds the Claude Free MCP sequence from catalog discovery to HTML and native OAC dashboards. Client setup is pre-work; all participants compare and validate the outputs. Expression Assistant retains a validated calculation fallback after a generation error. Participant sharing, an active workshop instance, a second-account rehearsal and capacity checks remain event readiness gates.

## Run the workshop

| Minutes | Activity | Instructions |
| --- | --- | --- |
| 0–10 | Lab 0 Get ready for the MPHA workshop | [Lab 0 Get ready for the MPHA workshop](labs/lab-00-start.md) |
| 10–25 | Lab 1 Prepare a dataset with Dataset Assistant | [Lab 1 Prepare a dataset with Dataset Assistant](labs/lab-01-dataset-assistant.md) |
| 25–35 | Lab 2 Generate a catalog description | [Lab 2 Generate a catalog description](labs/lab-02-catalog.md) |
| 35–45 | Lab 3 Enrich the metadata used by AI | [Lab 3 Enrich the metadata used by AI](labs/lab-03-enrichments.md) |
| 45–65 | Lab 4 Build a chart with Workbook Assistant | [Lab 4 Build a chart with Workbook Assistant](labs/lab-04-workbook.md) |
| 65–80 | Lab 5 Validate a denial-rate calculation | [Lab 5 Validate a denial-rate calculation](labs/lab-05-expression.md) |
| 80–90 | Take a ten minute break | [Take a ten minute break](labs/break.md) |
| 90–115 | Lab 6 Build and run a rollup with Data Flow Assistant | [Lab 6 Build and run a rollup with Data Flow Assistant](labs/lab-06-dataflow.md) |
| 115–130 | Lab 7 Watch the Semantic Modeler Assistant demo | [Lab 7 Watch the Semantic Modeler Assistant demo](labs/lab-07-semantic.md) |
| 130–145 | Lab 8 Add and challenge a Language Narrative | [Lab 8 Add and challenge a Language Narrative](labs/lab-08-narrative.md) |
| 145–175 | Lab 9 Create executive dashboards with Claude and OAC MCP | [Lab 9 Create executive dashboards with Claude and OAC MCP](labs/lab-09-mcp-claude.md) |
| 175–180 | Finish with a claims analysis checkpoint | [Finish with a claims analysis checkpoint](labs/lab-09-capstone.md) |

## Prepare and review

- [Facilitator run of show and readiness gates](FACILITATOR.md)
- [Live asset inventory and rehearsal evidence](PREPARATION_STATUS.md)
- [Semantic save failure reproduction record](SEMANTIC_SAVE_REPRO.md)
- [Git integration notes](GIT_INTEGRATION.md)
- [Source references](SOURCES.md)
- [Screenshot manifest](screenshots.json)
- [Downloaded OAC output checkpoint](checkpoints/MPHA_Claims_Rollup_Seed.csv)
- [Verification results](checkpoints/validation.json)
- [Original-schema read-only checks](sql/OAC_AILH_Semantic_Model_ReadOnly_Checks.sql)
- [New semantic-schema acceptance checks](sql/ORIGAMI_P01_ReadOnly_Acceptance.sql)
- [Industry semantic model evidence and limits](INDUSTRY_SEMANTIC_DEMO.md)
- [Inspected exported semantic model source](checkpoints/industry-semantic-model/physical/MPHA_AILH.json)
- [Build a local reset archive from the exported source](scripts/build_model_archive.py)
- [Rehearsal workbook formulas](sql/workbook_calculations.txt)
- [Claude MCP setup and artifact files](mcp/README.md)
- [Reviewed executive HTML](mcp/MPHA_Executive_Overview.html)
- [Native workbook JSON](mcp/MPHA_MCP_Executive_Native.workbook.json)
- [MCP live verification](mcp/verification.json)
- [Package verification script](verify_package.py)

Hands-on labs rehearsed on 19 October and Industry Analytics demo on 20 October 2026, Asia/Kolkata. Participant navigation uses Home search and assigned names; the instructor demo includes its private Industry Analytics model link. Review live tenant references and identity visible in screenshots before Git publication. Keep passwords and wallet files out of the workshop repository.


## Workshop publication

This module is integrated under [MPHA Lab 8 - AI Powered Business Analytics](https://jayaramu24.github.io/public-healthcare-AIDP-workshop/#lab8) on 21 October 2026. Tenant and account references are rehearsal examples. Use the assigned workshop configuration; private OAC assets are not made public by publishing this guide.
