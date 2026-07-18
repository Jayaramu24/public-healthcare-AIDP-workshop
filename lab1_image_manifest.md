# Lab 1 Image Manifest

This manifest is a control sheet for `Lab 1: Set Up Core Resources` in the Public Healthcare AIDP Workshop.

Its purpose is to prevent screenshot mix-ups by forcing each image to be mapped to exactly one workshop step before it is used in any HTML mockup or final workshop page.

## Status key

- `approved`: safe to use for the named Lab 1 step
- `candidate`: may be usable, but needs confirmation before use
- `reject`: do not use for Lab 1

## Manifest

| File | Current source area | What the image actually appears to show | Intended Lab 1 step | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `assets/oci_agent_lab/aidp_catalogs.png` | AIDP asset pool | AIDP master catalog / volume-style screen with Bronze, Silver, and Gold-style catalog entries visible in the left navigation | AIDP navigation or catalog setup reference | `approved` | Use only for AIDP catalog / volume context. Do not use for Object Storage, OAC, or AI Lakehouse. |
| `assets/oci_agent_lab/aidp_notebooks_folder.png` | AIDP asset pool | AIDP workspace folder tree with notebook folders shown in the left pane and content panel on the right | Not a Lab 1 setup step; useful later in Lab 2 | `reject` | Keep for Lab 2 only. |
| `assets/oci_agent_lab/aidp_workflow.png` | AIDP asset pool | A workflow/task orchestration canvas with connected nodes | Not a Lab 1 setup step; possibly later for orchestration explanation | `reject` | Do not use in Lab 1. |
| `assets/oci_agent_lab/aidp_ai_agent_flow.png` | Agent asset pool | Agent/demo experience screen, not a clear OCI setup image | None | `reject` | Not suitable for Lab 1 setup screenshots. |
| `assets/oci_agent_lab/oci_create_agent_reference.png` | Agent asset pool | Likely OCI agent creation/configuration screen | None | `reject` | Optional agent-lab material, not Lab 1. |
| `assets/oci_agent_lab/oci_create_endpoint_reference.png` | Agent asset pool | Likely endpoint creation/configuration screen | None | `reject` | Optional agent-lab material, not Lab 1. |
| `assets/oci_agent_lab/oci_create_knowledge_base_reference.png` | Agent asset pool | Likely knowledge base creation screen | None | `reject` | Optional agent-lab material, not Lab 1. |
| `assets/oci_agent_lab/oci_create_rag_tool_reference.png` | Agent asset pool | Likely RAG tool setup screen | None | `reject` | Optional agent-lab material, not Lab 1. |
| `assets/oci_agent_lab/oci_create_sql_tool_reference.png` | Agent asset pool | Likely SQL tool configuration screen, not a clean AI Lakehouse provisioning image | None for Lab 1 | `reject` | Do not use as a substitute for AI Lakehouse setup. |
| `assets/oci_agent_lab/oci_genai_playground_experience_reference.png` | Agent asset pool | OCI Generative AI Playground / copilot-style chat experience | None | `reject` | Optional agent-lab material, not Lab 1. |
| `assets/oci_agent_lab/oci_genai_playground_test_reference.png` | Agent asset pool | Generative AI playground / test prompt screen | None | `reject` | Optional agent-lab material, not Lab 1. |
| `assets/oac_dashboard_lab/oac_reference_layout.png` | OAC asset pool | OAC-style workbook layout with assistant sidecar | OAC purpose / guided workbook context only | `candidate` | Only use at the very end of Lab 1 to explain what OAC will later be used for. Not a true provisioning screenshot. |
| `assets/oac_dashboard_lab/oac_claims_overview.png` | OAC asset pool | Workshop-generated OAC claims overview screen | None for Lab 1 | `reject` | Use in Lab 4 only. |
| `assets/oac_dashboard_lab/oac_denial_analysis.png` | OAC asset pool | Workshop-generated OAC denial analysis screen | None for Lab 1 | `reject` | Use in Lab 4 only. |
| `assets/oac_dashboard_lab/oac_program_performance.png` | OAC asset pool | Workshop-generated OAC program performance screen | None for Lab 1 | `reject` | Use in Lab 4 only. |

## Clean Lab 1 usable set right now

Based on the current local asset pool, the only clearly defensible Lab 1 product screenshot we should use right now is:

1. `assets/oci_agent_lab/aidp_catalogs.png`

And the only conditional / contextual image we may use at the end of Lab 1 is:

2. `assets/oac_dashboard_lab/oac_reference_layout.png`

Everything else currently available in the local asset pool should be treated as out of scope for Lab 1.

## Gap list for Lab 1

The following real setup screenshots are still missing from the local approved set and should be sourced cleanly before Lab 1 is rebuilt:

1. OCI Object Storage bucket creation
2. OCI Object Storage folder creation
3. AIDP create instance screen
4. AIDP standard policy selection screen
5. Autonomous AI Lakehouse create instance screen
6. Database Actions / SQL screen for the Gold-serving schema
7. OAC create instance screen

## Rule for the next mockup

Do not build another Lab 1 screenshot mockup until each image used in it appears in this manifest with status `approved`.
