# Public Healthcare AIDP workshop - execution pack

Use the HTML/PDF guide for the required lab sequence; OAC is at the end.

1. Start from your preloaded participant folder. Restore only missing notebooks.
2. If restoring, unzip this pack, use AIDP Upload in your own named folder, and
   set the configuration values from participant_configuration.md in each file.
3. Run notebooks 01 -> 02 -> 03 -> 04 manually; validate the Claims star schema.
4. Run 02B and 03B after the context DDL/admin catalog-refresh handoff.
5. Run 05 for historical train/test/evaluate/score/reload; register its real fitted model.
6. Build the five-task workflow only after manual runs pass. RAG/agent testing is separate.
7. Use 99 only when you want sample rows, persisted counts or distinct values.

Notebook numbers identify files, not labs. SQL files run in Oracle Database
Actions as the assigned schema owner, not ADMIN. Do not grant wide privileges,
truncate tables or overwrite other participants' output. The supplied loader
is safe for same-input reruns, not general CDC or changing dimension keys.

The pack deliberately excludes obsolete ML, Kafka/GoldenGate and bulk-admin
scripts. ML scores stay in your volume; no automatic ML score serving in OAC.
See VALIDATION_NOTES.md for verified evidence and remaining readiness checks.


Lab 8 now links to the three-hour OAC AI program. The separate `downloads/MPHA_OAC_AI_LiveLabs_Runbook.zip` contains its HTML/Markdown guide, screenshots and Claude MCP artifacts; it is included in the offline review bundle. Extract it and open `oac-ai-workshop/index.html`. Client configuration and participant access are pre-work.


## OAC revision — 22 October 2026
Lab 8 contains all OAC instructions inline. Reuse the supplied AILH connection and start with flattened MPHA_OAC_STAR_CLAIMS (19  fields). Use the pre-discovered prepared base for Auto Insights, retained successful AI examples and rollup/MCP; make private copies for metadata edits. Auto Insights and column Explain precede Workbook Assistant. Contextual Explain, drill and Forecast are followed by data flows, narratives and HTML-to-native JSON/MCP writes. The guide retains successful19–22 October evidence and omits unsuccessful generation paths. Core 180 minutes excludes dimensional DIY and the final Industry Analytics semantic demo. See [Lab 8](index.html#lab8) and [evidence](oac-ai-workshop/PREPARATION_STATUS.md).
