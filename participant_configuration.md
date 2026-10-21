# Participant configuration handoff

Completed privately by the administrator. Example names in screenshots are illustrative.
No passwords, secrets, wallet contents or access tokens belong in this file.

| Value | Assigned value |
|---|---|
| AIDP login URL and region | Administrator supplies |
| Workspace | Administrator supplies |
| participant_id / named folder | Administrator supplies |
| Spark compute / AI compute | Administrator supplies |
| volume_base: exact shared raw /Volumes mount | Administrator supplies |
| output_base: exact personal /Volumes mount | Administrator supplies |
| target_catalog: external Lakehouse catalog | Administrator supplies |
| target_schema / Database Actions username and URL | Administrator supplies |
| table_prefix | mpha |
| Standard catalog and schema for models/KB | Administrator supplies |
| Experiment | MPHA_<participant_id>_Claims_Denial_Risk |
| Model name | Unique administrator-approved participant model name |
| Knowledge base and agent name | Unique administrator-approved participant names |
| Approved LLM region/model | Administrator supplies; Osaka/Command A is a tested example |
| OAC URL / connection / workbook | Administrator supplies |

Shared raw volume children: raw/, raw_json/, raw_spatial/, documents/.
Personal output volume children: bronze/, silver/, gold_stage/, ml/.
These are separate mounts even if the underlying bucket is shared.
The administrator creates IAM/AIDP permissions; a folder name or Python guard
does not enforce isolation. Check with a participant account, not ADMIN.

Keep preloaded values when they match this handoff. Restored common downloads
fail until placeholders are replaced. Save settings in every notebook before
workflow execution: interactive variables do not carry between tasks.


## Lab 8 OAC AI and Claude MCP pre-work

- Receive the assigned OAC URL, personal author account, released claims dataset/seed access and your P01-P20 identifier. Rehearsal asset names and private OAC URLs are examples, not participant access grants.
- Confirm the 20 prepared data elements, helper numerator and baseline totals in the [OAC runbook](oac-ai-workshop/index.html#lab-00-start). Use actual dataset IDs when adapting workbook JSON.
- The instructor alone uses Industry Analytics and its semmodel System connection for Semantic Modeler. Participants stay in the assigned hands-on instance.
- For the Claude exercise, follow [local MCP setup](oac-ai-workshop/mcp/README.md) before class. Use your own approved client and OAC account, private target folder and unique workbook names. Do not share logins or paste credentials into prompts.
- Confirm the approved scope for sending synthetic aggregate query results to Claude. Reuse the supplied files to conserve Free-plan allowance. Participants without a configured client still compare the supplied HTML and OAC native results.
- The three-hour program includes a ten-minute break. Connection provisioning and client installation are outside that timebox. The facilitator must rehearse access with a second account and test classroom capacity.
