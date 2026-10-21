# Validation scope and readiness checks

This edition includes the approved required-lab sequence, illustrative deployment
names and AI Powered Business Analytics as the final lab. All source data is
synthetic. Lab 0 is administrator-owned; participant access remains scoped.

## Verified reference execution
- The reference five-task workflow completed Bronze, Silver, Gold, Lakehouse
  load and ML successfully. Context extension and agents are separate exercises.
- Claims: 622 fact rows, 1,400 submitted claims, 121 denied, submitted amount
  1,239,912.67. Reference-key and grain checks passed on the supplied snapshot.
- ML: 303 training, 110 held-out test and 102 batch-score rows. The fitted artifact
  was logged/reloaded successfully; an interactive run was registered. A new
  workflow run does not automatically register a model version.
- Combined SQL/RAG agent testing invoked both tools successfully. SQL executes
  a predefined query; it is not an arbitrary natural-language SQL agent.

## Before delivering this workshop
- Generic notebook downloads have explicit configuration placeholders and were
  syntax-checked, but were not rerun as newly imported generic downloads in this
  documentation revision. Validate an import with an isolated test participant.
- Verify effective folder, volume, catalog, compute, model and KB permissions
  with a participant account. Admin visibility does not prove isolation.
- Earlier context, KB and OAC screenshots remain product references, not fresh
  execution evidence for every tenancy. Validate assigned connections locally.
- Fresh Database Users/privilege and participant-permission form screenshots
  remain a documentation follow-up. Existing result screens do not show all
  creation fields. Follow administrator instructions rather than copying names.
- Lab 8 navigation, runbook links and screenshot loading were checked in the browser during the OAC integration; the updated PDF pages were rendered and inspected.

## Boundaries
- Snapshot overwrites and missing-key append are not CDC and do not handle
  changing dimension keys or revised fact measures without a reviewed strategy.
- ML recall is 0.105 at threshold 0.5: a teaching baseline, not production claims
  decisioning. Scores stay in participant storage, not automatically in OAC.
- Agent validation is in Playground, not a production endpoint. Operational
  actions and claims decisions remain human-owned.
- Facility Access Daily is an independent design challenge, not a supplied or
  verified end-to-end Facility loader.


## OAC AI module integrated 21 October 2026

- The new three-hour program is linked from Lab 8, README, downloads and the single-flow/Markdown guide. It includes 76 unedited screenshots: 71 browser captures at 1920 x 1080 and five native Claude captures at 2400 x 1600.
- Actual rehearsal on 19-20 October verified dataset naming/type recommendations, catalog descriptions, reviewed AI metadata/indexing, workbook charts, a completed rollup flow, narratives and the Industry Analytics semantic metadata demo. Expression Assistant generation failed; the manual expression produced 8.64%.
- Claude Desktop Free discovered the claims datasets, queried 30 district-month rows and generated HTML. Two private workbooks were created through MCP. The HTML iframe and native visuals matched totals and Central City filters; district ratios were corrected to their explicit aggregation grain before delivery.
- The native workbook source, HTML snapshot and local compatibility helper are teaching artifacts. They need actual destination dataset references and template compatibility checks when moved between accounts/tenants. No authentication runtime or Oracle utility is redistributed.
- Publication does not establish participant permissions, repair the original semantic-save defect, deploy the Industry model, or validate 15-20 concurrent authors. See [module status](oac-ai-workshop/PREPARATION_STATUS.md) for remaining gates.


## OAC revision — 22 October 2026
Lab 8 contains all OAC instructions inline. Reuse the supplied AILH connection and start with flattened MPHA_OAC_STAR_CLAIMS (19  fields). Use the pre-discovered prepared base for Auto Insights, retained successful AI examples and rollup/MCP; make private copies for metadata edits. Auto Insights and column Explain precede Workbook Assistant. Contextual Explain, drill and Forecast are followed by data flows, narratives and HTML-to-native JSON/MCP writes. The guide retains successful19–22 October evidence and omits unsuccessful generation paths. Core 180 minutes excludes dimensional DIY and the final Industry Analytics semantic demo. See [Lab 8](index.html#lab8) and [evidence](oac-ai-workshop/PREPARATION_STATUS.md).
