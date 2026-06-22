# Optional Lab 6 - Claims and Policy Copilot

## Goal

Build a copilot that can answer claims, payment, membership, provider-accreditation, and policy questions by combining SQL over the Gold layer with grounded retrieval over the MPHA playbook.

## Implementation note

Oracle's March 31, 2026 AI Data Platform Workbench blog presents AI Agent Flow as planned for a future GA release. For a runnable workshop pattern today, use AI Data Platform to prepare the data and OCI Generative AI Agents to expose the executable SQL-plus-RAG copilot.

The screenshots below use a blend of official Oracle references and workshop visuals:

- Oracle AI Data Platform Workbench blog visuals for the AIDP preparation and orchestration flow
- Oracle Cloud Infrastructure documentation pages as the reference visuals for the Generative AI Agents console steps
- Representative OCI Generative AI playground-style visuals for the testing and exposed-chat experience in Steps 8 and 9

## Business Scenario

MPHA wants claims leaders and policy teams to ask questions such as:

- Which districts have the highest denial exposure this month?
- Which programs have the biggest submitted-to-paid gap?
- Which claim types are taking the longest to adjudicate?
- What does the playbook recommend when denial rate and processing days rise together?
- Which provider-accreditation risks should policy teams review first?

## Required workshop assets

- Claims star schema Gold objects in AI Lakehouse
- `data/gold/gold_claims_denial_risk_scores.csv` or its equivalent table
- `documents/MPHA_Winter_Respiratory_Response_Playbook.docx`
- Optional text or PDF exports of the same policy content for easier knowledge-base ingestion

## Prerequisites

Before starting the copilot build, confirm:

- the Claims star schema objects are already queryable in Autonomous AI Lakehouse
- the playbook document is available in Object Storage
- the facilitator can access OCI Generative AI Agents in the correct compartment
- the SQL-serving scope for the workshop has already been agreed
- the optional ML output is available if you want the copilot to answer risk-prioritization questions

## Step-by-step build process

### Step 1 - Prepare the SQL-serving layer

Create or validate a compact claims-serving set in AI Lakehouse:

- `MPHA_FACT_CLAIMS_MONTHLY`
- `MPHA_FACT_DISBURSEMENT_MONTHLY`
- `MPHA_FACT_MEMBERSHIP_SNAPSHOT`
- `MPHA_FACT_PROVIDER_ACCREDITATION`
- `MPHA_GOLD_CLAIMS_DENIAL_RISK_SCORES`

Keep the SQL scope tight. This agent should answer payer and policy questions, not every possible healthcare question in the lakehouse.

![AIDP catalogs reference](assets/oci_agent_lab/aidp_catalogs.png)

Source: [Oracle AI Data Platform Workbench blog - AI Data Platform Workbench Catalogs](https://blogs.oracle.com/ai-data-platform/oracle-ai-data-platform-workbench-drive-ai-powered-workflows-and-insights-across-enterprise-and-oracle-fusion-cloud-erp-data)

Execution checklist:

1. Validate that the claims, disbursement, membership, accreditation, and optional scoring tables are populated.
2. Confirm the table and column names that the SQL tool will expose.
3. Keep the SQL scope limited to the workshop-serving layer rather than exposing unrelated schemas.

### Step 2 - Prepare the knowledge source

Stage the MPHA playbook in Object Storage for retrieval:

- keep the document in a dedicated bucket or prefix
- use the single playbook as the authoritative policy source for the workshop
- confirm that section titles and page references are preserved

![AIDP notebooks folder reference](assets/oci_agent_lab/aidp_notebooks_folder.png)

Source: [Oracle AI Data Platform Workbench blog - AI Data Platform Workbench Notebooks](https://blogs.oracle.com/ai-data-platform/oracle-ai-data-platform-workbench-drive-ai-powered-workflows-and-insights-across-enterprise-and-oracle-fusion-cloud-erp-data)

Execution checklist:

1. Place the playbook in a dedicated bucket or prefix.
2. If needed, also create a PDF or text copy for easier ingestion.
3. Confirm the document title, section names, and page structure are preserved so citations remain meaningful.

### Step 3 - Create the knowledge base

In OCI Generative AI Agents:

1. Create a knowledge base.
2. Choose Object Storage as the data-store type.
3. Select the bucket or prefix that contains the policy document.
4. Start the ingestion job so the knowledge base becomes queryable.

![Create knowledge base reference](assets/oci_agent_lab/oci_create_knowledge_base_reference.png)

Source: [OCI Generative AI Agents documentation - Creating a Knowledge Base](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/create-knowledge-base.htm)

Execution checklist:

1. Name the knowledge base clearly, such as `MPHA_Playbook_KB`.
2. Select the Object Storage location that contains the policy source.
3. Start ingestion and wait for the job to complete before testing the agent.
4. Validate that the knowledge base is queryable and ready to attach to a tool.

### Step 4 - Create the agent shell

Create an agent with:

- a clear name such as `MPHA_Claims_Policy_Copilot`
- a welcome message that sets the scope
- routing instructions such as: `Use the SQL tool first for metrics. Use the RAG tool for policy guidance. Use both when the user asks what happened and what action is recommended.`

![Create agent reference](assets/oci_agent_lab/oci_create_agent_reference.png)

Source: [OCI Generative AI Agents documentation - Creating an Agent](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/create-agent.htm)

Execution checklist:

1. Create the agent shell first before adding tools.
2. Set a short description that explains the copilot's scope to workshop participants.
3. Add instructions that tell the agent when to prefer SQL, when to prefer RAG, and when to combine both.

### Step 5 - Add the SQL tool

Configure a SQL tool for the claims-serving layer:

1. Import the schema inline or from Object Storage with table, column, and relationship definitions.
2. Select `Oracle SQL` as the dialect.
3. Add in-context examples for claims, payment, and denial questions.
4. Attach a database connection if you want live execution.
5. Enable SQL execution.
6. Enable SQL self-correction if you want the agent to repair failed queries.

Suggested examples:

- Question: Which districts have the highest denial rate in June 2025?
- Question: Which coverage programs have the largest submitted-to-paid gap?
- Question: Which claim types are driving the highest pending volume?

![Create SQL tool reference](assets/oci_agent_lab/oci_create_sql_tool_reference.png)

Source: [OCI Generative AI Agents documentation - Creating a SQL Tool](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/sqltool-add.htm)

Execution checklist:

1. Load the schema metadata for the approved claims-serving tables.
2. Add two or three good in-context examples before enabling execution.
3. Test a simple aggregation question first.
4. Test a more complex question that compares multiple programs or districts.

### Step 6 - Add the RAG tool

Create a RAG tool and attach the MPHA playbook knowledge base:

- set custom instructions to answer with concise policy guidance
- ask the tool to cite the relevant section or page when possible
- keep the tone operational rather than clinical

![Create RAG tool reference](assets/oci_agent_lab/oci_create_rag_tool_reference.png)

Source: [OCI Generative AI Agents documentation - Creating a RAG Tool](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/RAG-tool-create.htm)

Execution checklist:

1. Attach the knowledge base created in Step 3.
2. Add guidance telling the tool to cite the relevant section or page.
3. Test a policy-only question before combining it with SQL-backed questions.

### Step 7 - Create the endpoint

Create an endpoint for the agent so the team can test it interactively:

- enable human in the loop if the workshop team wants a review step
- keep moderation settings aligned with the demo environment

![Create endpoint reference](assets/oci_agent_lab/oci_create_endpoint_reference.png)

Source: [OCI Generative AI Agents documentation - Creating an Endpoint](https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/create-endpoint.htm)

Execution checklist:

1. Create the endpoint only after the SQL and RAG tools are attached.
2. Confirm the endpoint is reachable from the intended demo environment.
3. Keep security and moderation settings aligned with the workshop setup.

### Step 8 - Test with combined questions

Use prompts that require both data and policy grounding:

- `Which districts have the highest denial exposure in June 2025 and what action does the playbook recommend?`
- `Which coverage programs have the biggest submitted-to-paid gap and what operating follow-up should claims leaders run?`
- `Which provider-accreditation risks line up with high denial pressure?`

![Generative AI playground combined-question reference](assets/oci_agent_lab/oci_genai_playground_test_reference.png)

Reference visual: workshop-created OCI Generative AI playground-style view aligned to the combined-question testing experience.

Execution checklist:

1. Test one SQL-only question.
2. Test one RAG-only policy question.
3. Test one combined question that needs both claims metrics and playbook guidance.
4. Verify that the answer uses the right tool path and stays within the workshop scope.

### Step 9 - Expose the experience

Use the endpoint in a lightweight chat experience or as a sidecar assistant pattern during the workshop. Position it as a copilot for claims and policy teams, not a replacement for governed dashboards.

![Generative AI playground exposed experience reference](assets/oci_agent_lab/oci_genai_playground_experience_reference.png)

Reference visual: workshop-created OCI Generative AI playground-style view aligned to the exposed copilot chat experience.

## Facilitator run sequence

Use this exact order during the workshop:

1. Show the claims-serving tables that power the SQL tool.
2. Show the playbook document that powers the knowledge base.
3. Show the knowledge base creation result.
4. Show the agent shell and tool attachments.
5. Run one SQL-backed question.
6. Run one playbook-backed policy question.
7. Run one combined claims-and-policy question.
8. Close by explaining how this differs from OAC Assistant:
   - OAC Assistant works on the indexed analytics dataset
   - the copilot combines governed SQL plus playbook retrieval for broader operational guidance

## Expected outcome

You can show a practical agent pattern for this workshop: AI Data Platform creates the trusted Gold layer, OCI Generative AI Agents supplies the executable copilot today, and the answer path stays grounded in both curated claims data and the MPHA playbook.
