# Lab 6 - Claims and Policy Copilot in AIDP

## Goal

Build an Oracle AI Data Platform agent flow that can answer MPHA claims analytics and policy questions by combining:

- SQL over the Claims star schema in Autonomous AI Lakehouse
- RAG over the MPHA Winter Respiratory Response Playbook
- Supervisor-agent routing that decides whether to call SQL, RAG, or both

## Business scenario

MPHA claims leaders want to ask:

- Which districts have the highest denial exposure?
- Which coverage programs or claim types are driving the submitted-to-paid gap?
- What does the MPHA playbook recommend when respiratory emergency visits and facility occupancy rise?
- How should operations respond when high-denial districts also face facility pressure?

## Admin prerequisites

Before participants build or test the agent, the facilitator confirms:

1. The Claims star schema is loaded and validated in AI Lakehouse:
   - `mpha_fact_claims_monthly`
   - `mpha_dim_date`
   - `mpha_dim_district`
   - `mpha_dim_coverage_program`
   - `mpha_dim_claim_type`
2. AIDP can read the AI Lakehouse external catalog and assigned participant schema, for example `goldailh.MPHA_P17`.
3. The MPHA playbook is indexed in the AIDP knowledge base prepared in Part A, for example `e2eindustrydemos.default.mphapolicy`.
4. The facilitator created a blank `MPHA_Claims_Policy_Copilot` shell in Lab 0.
5. The Lab 0 AI compute `AIComputeForAgents` is active or available to attach from the shell **Compute** menu.
6. The user has access to the AIDP workspace `E2EAIDPIndustryDemos`.

## Part A - Prepare the MPHA playbook knowledge base

Use this part when the facilitator has not already prepared the `mphapolicy` knowledge base.

### Step A1 - Open the standard catalog schema

In AIDP Workbench, click **Master catalog**, open the standard catalog `e2eindustrydemos`, and open schema `default`.

Confirm the schema includes **Volumes**, **Knowledge Bases**, and **Models**.

![AIDP schema types with Knowledge Bases](assets/aidp_rag_knowledge_lab/screenshots/03_schema_types_knowledge_bases_visible.png)

Expected result: participants know where the knowledge base will be created.

### Step A2 - Confirm the external volume and playbook file

Open **Volumes** and confirm `e2eindustrydemovol` is listed as an **External** volume.

![External volume for MPHA document source](assets/aidp_rag_knowledge_lab/screenshots/04_external_volume_for_playbook_source.png)

Open `e2eindustrydemovol`, then open `documents`. Confirm the folder contains `MPHA_Winter_Respiratory_Response_Playbook.docx`.

![MPHA playbook file in documents](assets/aidp_rag_knowledge_lab/screenshots/06_rawdata_playbook_docx_visible.png)

Expected result: the playbook document is available through `/Volumes/e2eindustrydemos/default/e2eindustrydemovol/documents`.

### Step A3 - Create the knowledge base shell

Return to `e2eindustrydemos.default`, click **Add to schema**, and choose **Knowledge base**.

![Add Knowledge base from schema](assets/aidp_rag_knowledge_lab/screenshots/12_add_to_schema_knowledge_base_menu.png)

Create the knowledge base with these values:

- Name: `mphapolicy`
- Description: `MPHA playbook knowledge base for claims policy copilot`
- Workspace for compute: `E2EAIDPIndustryDemos`
- Cluster used for ingestion: the active workshop Spark cluster
- Embedding model: use the model enabled for the workshop environment
- Chunk size: default unless the facilitator specifies a different value
- Chunk overlap: default unless the facilitator specifies a different value

![Create Knowledge Base dialog](assets/aidp_rag_knowledge_lab/screenshots/13_create_knowledge_base_dialog_advanced_settings.png)

Expected result: `e2eindustrydemos.default.mphapolicy` exists as a knowledge base.

### Step A4 - Add documents as the data source

Open `mphapolicy`, go to the **Data Source** tab, and click **Add data source to knowledge base**.

In the tree selector, choose the documents folder from the external volume:

`/Volumes/e2eindustrydemos/default/e2eindustrydemovol/documents`

Keep **DOCX** selected. It is acceptable to keep PDF and TEXT selected if the folder may later include those supported file types. Keep **Start ingestion job on add** selected for the workshop.

![Add data source dialog](assets/aidp_rag_knowledge_lab/screenshots/14_add_data_source_dialog_file_filters_ingestion.png)

Expected result: the `documents` folder appears as a volume data source for `mphapolicy`.

### Step A5 - Validate parameters and run ingestion

Open the `documents` data source from the knowledge base.

Confirm:

- Path: `/Volumes/e2eindustrydemos/default/e2eindustrydemovol/documents`
- File pattern includes `docx`
- Workspace and cluster keys are populated

If ingestion did not start automatically, click **Ingest now**.

![Knowledge base data source row](assets/aidp_rag_knowledge_lab/screenshots/08_mphapolicy_data_source_rawdata_volume.png)

Open the data source parameters panel and verify the ingestion controls before continuing.

![Knowledge base data source parameters](assets/aidp_rag_knowledge_lab/screenshots/09_kb_data_source_parameters_ingest_now.png)

Expected result: the playbook source is ready to be chunked and embedded.

### Step A6 - Verify ingestion succeeded

Open the **Job runs** tab for the `documents` source and confirm the latest run shows **Succeeded**.

![Knowledge base ingestion succeeded](assets/aidp_rag_knowledge_lab/screenshots/10_kb_ingestion_job_runs_succeeded.png)

Open the knowledge-base **Details** tab if you need to confirm the workspace and cluster keys.

![Knowledge base details](assets/aidp_rag_knowledge_lab/screenshots/11_mphapolicy_knowledge_base_details.png)

Expected result: `e2eindustrydemos.default.mphapolicy` is ready for the RAG tool in Part B.

## Part B - Build and test the copilot agent

### Step 1 - Open Agent flows

In AIDP Workbench, open the shared workspace and click **Agent flows**.

![AIDP Agent flows landing page](assets/aidp_agent_lab/screenshots/00_agent_flows_landing_page.png)

Expected result: the participant can see the existing or newly created `MPHA_Claims_Policy_Copilot` flow.

### Step 2 - Open the prepared copilot shell

Open the prepared blank visual flow from Lab 0. If the facilitator did not run Lab 0, create a new visual flow with the same name.

Use:

- Flow name: `MPHA_Claims_Policy_Copilot`
- Authoring mode: Visual
- Starting pattern: empty shell with no supervisor, executor agents, SQL tool, or RAG tool

![Blank AIDP Claims Policy Copilot shell](assets/aidp_agent_lab/screenshots/10c_blank_agent_flow_shell_created_no_compute.png)

Expected result: participants start from the blank shell and build the copilot logic themselves.

### Step 3 - Configure the supervisor agent

Name the supervisor:

`SUPERVISOR_AGENT_1`

Use this routing pattern:

```text
Available executor agents:
- AGENT_1: structured MPHA claims analytics from the AI Lakehouse Claims star schema.
- AGENT_2: document-grounded MPHA policy, playbook, accreditation, prior authorization, denial remediation, disbursement, membership, and facility-pressure guidance.
- For structured claims questions, call AGENT_1.
- For document or policy questions, call AGENT_2.
- For combined data-plus-policy questions, call AGENT_1 first, then AGENT_2, then synthesize both results.
- Do not call SQL_1 or RAG_1 directly from the supervisor.
```

![Supervisor agent instructions](assets/aidp_agent_lab/screenshots/02_supervisor_agent_instructions.png)

Expected result: the supervisor routes claims metrics to the SQL executor, policy questions to the RAG executor, and combined questions to both.

### Step 4 - Configure the Claims SQL executor

Name the executor:

`AGENT_1`

Purpose:

`Claims SQL executor for denial-rate, payment, district, program, claim type and processing-day metrics.`

Mandatory behavior:

```text
- Always call SQL_1 before answering any structured claims analytics question.
- Use SQL_1 for questions about claims submitted, denied claims, denial rate, submitted amount, paid amount, processing days, district hotspots, coverage program performance, claim type patterns, or monthly trends.
- Use only rows returned by SQL_1.
- If SQL_1 fails or returns no rows, say the SQL tool failed or returned no rows.
```

![SQL executor instructions](assets/aidp_agent_lab/screenshots/03_sql_agent_instructions.png)

Expected result: `AGENT_1` is connected only to `SQL_1`.

### Step 5 - Configure the Claims star schema SQL tool

Name the SQL tool:

`SQL_1`

Purpose:

Retrieve MPHA claims denial hotspots from the AI Lakehouse Claims star schema.

Use this query shape:

```sql
SELECT
  d.full_date AS service_month,
  di.district_name,
  p.coverage_program,
  c.claim_type,
  SUM(f.claims_submitted) AS claims_submitted,
  SUM(f.denied_claims) AS denied_claims,
  ROUND((SUM(f.denied_claims) * 100.0) /
        CASE WHEN SUM(f.claims_submitted) = 0 THEN NULL ELSE SUM(f.claims_submitted) END, 2) AS denial_rate_pct,
  ROUND(SUM(f.total_submitted_amount), 2) AS total_submitted_amount,
  ROUND(SUM(f.total_paid_amount), 2) AS total_paid_amount,
  ROUND(AVG(f.avg_processing_days), 1) AS avg_processing_days
FROM mpha_fact_claims_monthly f
JOIN mpha_dim_date d ON f.service_month_date_key = d.date_key
JOIN mpha_dim_district di ON f.district_key = di.district_key
JOIN mpha_dim_coverage_program p ON f.program_key = p.program_key
JOIN mpha_dim_claim_type c ON f.claim_type_key = c.claim_type_key
GROUP BY d.full_date, di.district_name, p.coverage_program, c.claim_type
ORDER BY denial_rate_pct DESC, denied_claims DESC
FETCH FIRST :TOP_N ROWS ONLY
```

![Claims star schema SQL tool](assets/aidp_agent_lab/screenshots/04_sql_tool_claims_star_query.png)

Expected result: the tool returns service month, district, coverage program, claim type, denied claims, denial rate, submitted amount, paid amount, and average processing days.

### Step 6 - Configure the Policy RAG executor

Name the executor:

`AGENT_2`

Purpose:

Answer MPHA policy, playbook, accreditation, prior authorization, denial remediation, disbursement, membership, and facility-pressure questions.

Mandatory behavior:

```text
- Always call RAG_1 before answering.
- Use only evidence returned by RAG_1.
- If RAG_1 returns no relevant evidence, say the policy source does not contain enough evidence to answer this.
- Include source references when available.
```

![RAG executor instructions](assets/aidp_agent_lab/screenshots/05_rag_agent_instructions.png)

Expected result: `AGENT_2` is connected only to `RAG_1`.

### Step 7 - Configure the MPHA playbook RAG tool

Name the RAG tool:

`RAG_1`

Knowledge base:

`e2eindustrydemos.default.mphapolicy`

Purpose:

Retrieve MPHA playbook chunks for operational guidance, escalation thresholds, denial remediation, accreditation, membership operations, disbursement controls, and facility pressure.

![MPHA playbook RAG tool](assets/aidp_agent_lab/screenshots/06_rag_tool_playbook_knowledge_base.png)

Expected result: the tool returns ranked chunks with source paths and chunk references.

### Step 8 - Deploy the flow

1. Confirm the canvas wiring is complete.
2. On the agent flow page, click **Compute** and attach the Lab 0 compute `AIComputeForAgents` if it is not already attached.
3. Wait until the active AI compute badge appears. Playground and tool tests depend on this attached compute.
4. Click **Deploy**.
5. In the deployment dialog, select the AI compute that will host the deployed endpoint.
6. Deploy the flow and wait until the action button changes to **Undeploy**.

![Agent flow Compute menu](assets/aidp_agent_lab/screenshots/10_agent_compute_menu_create_attach.png)

Expected result: the Compute menu lets participants attach the compute prepared in Lab 0. Creating compute here is a fallback only if the facilitator skipped that admin step.

![Deployed AI compute state](assets/aidp_agent_lab/screenshots/07_deployed_ai_compute_active.png)

Expected result: the page shows `AIComputeForAgents (ACTIVE)` and the action button changes to `Undeploy`.

### Step 9 - Open Playground

1. Switch from **Development** to **Playground**.
2. Select `SUPERVISOR_AGENT_1`.
3. Create a clean test session.
4. Run the tests through the supervisor, not directly through the executor agents.

![Supervisor playground entry](assets/aidp_agent_lab/screenshots/08_supervisor_playground_entry.png)

Expected result: participants can test SQL-only, RAG-only, and combined prompts.

### Step 10 - Run the validation prompts

Run these three prompts in order.

| Test | Prompt | Expected path |
| --- | --- | --- |
| SQL-only | Identify the top 5 MPHA claims denial hotspots with district, coverage program, claim type, denied claims, denial rate, submitted amount, paid amount, and average processing days. | `SUPERVISOR_AGENT_1 -> AGENT_1 -> SQL_1` |
| RAG-only | What does the MPHA playbook recommend for rising respiratory emergency visits and high facility occupancy pressure? | `SUPERVISOR_AGENT_1 -> AGENT_2 -> RAG_1` |
| Combined | Use both agents. First identify the top 3 MPHA claims denial hotspots. Then retrieve general MPHA playbook actions for rising respiratory emergency visits and high facility occupancy pressure. Synthesize how operations should prioritize those high-denial districts if the same pressure conditions occur. | SQL first, RAG second, then supervisor synthesis |

![Combined supervisor response](assets/aidp_agent_lab/screenshots/09_supervisor_combined_test_response.png)

## Expected combined result

The validated workshop run returned:

| Evidence | Example result |
| --- | --- |
| Claims hotspot 1 | East River, Maternal and Child Health, Pharmacy: 3 denied claims, 100% denial rate, $368.62 submitted, $0 paid, 21.7 average processing days. |
| Claims hotspot 2 | East River, Chronic Care Support, Emergency: 2 denied claims, 100% denial rate, $2,044.29 submitted, $0 paid, 15.5 average processing days. |
| Claims hotspot 3 | Central City, Chronic Care Support, Diagnostic: 2 denied claims, 100% denial rate, $868.39 submitted, $0 paid, 22.5 average processing days. |
| Playbook evidence | Discharge acceleration, transfer review, flex clinical staffing, routing non-urgent demand to same-day clinics, mobile sessions, extended respiratory assessment hours, and weekly executive review. |
| Recommendation | Prioritize East River and Central City during respiratory surge or high occupancy pressure because they combine claims denial exposure with operational access risk. |

## Completion criteria

The lab is complete when:

1. SQL-only questions return claims hotspot data.
2. RAG-only questions return MPHA playbook evidence with sources.
3. Combined questions call both executor agents and return a synthesized action plan.
4. The supervisor does not bypass `AGENT_1` or `AGENT_2`.
