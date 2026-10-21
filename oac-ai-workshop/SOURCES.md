# Research sources

Primary Oracle documentation was reviewed against the actual tenants. The hands-on paths were exercised in the original OAC environment; the Semantic Modeler build and AI metadata paths were exercised in Industry Analytics on 20 October 2026. Documentation describes supported behavior, while the preparation status records the behavior actually observed. The Industry model remains private and undeployed.

## Scope and configuration

- [AI Assistant features](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acabi/oracle-analytics-ai-assistants-features.html)
- [Manage AI feature and model assignments](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acabi/manage-oracle-analytics-ai-assistants-models.html)
- [Generative AI FAQs](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acabi/faqs-oracle-analytics-generative-ai.html)
- [OAC release notes](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acswn/)

## Dataset metadata and preparation

- [Rename columns with Dataset Assistant](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/rename-columns-using-ai-assistant.html)
- [Change column types with Dataset Assistant](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/change-column-types-using-ai-assistant.html)
- [Catalog metadata generation](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/add-metadata-dataset-using-ai.html)
- [AI descriptions](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/ai-descriptions-datasets.html)
- [Add AI descriptions](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/add-ai-descriptions-dataset.html)
- [Dataset indexing](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/indexing-dataset-oracle-analytics-ai-assistant.html)
- [Duplicate datasets](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/duplicate-dataset.html)
- [Dataset permissions](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/add-or-update-datasets-permissions.html)

## Workbooks and calculations

- [Workbook Assistant](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/generate-visualizations-workbooks-oracle-analytics-ai-assistant.html)
- [Compose expressions](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/compose-expressions.html)
- [Calculation reuse](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/tips-using-calculations.html)
- [Logical SQL dataset qualification](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/logical-sql-execution-preview.html)
- [Oracle product-management article on Expression Assistant](https://blogs.oracle.com/analytics/create-custom-calculations-and-expression-filters-with-expression-assistant-in-oracle-analytics-cloud-workbooks)

## Data flows

- [Data Flow Assistant preview](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/use-ai-assistant-create-data-flows.html)
- [Enable Data Flow AI Assistant](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acabi/enable-data-flow-ai-assistant-preview.html)
- [Enable Expression Editor AI Assistant for Data Flows](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acabi/enable-expression-editor-ai-assistant-data-flows-preview.html)
- [Preview activation](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acabi/make-preview-features-available.html)
- [Create a dataset with a flow](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/create-dataset-using-data-flow.html)
- [Execute a data flow](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/generate-or-update-dataset-using-data-flow.html)

## Semantic modeling

- [System connection requirement](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/semantic-model-data-source-connections.html)
- [View available model connections](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/view-data-source-connections-available-semantic-models.html)
- [Semantic modeling workflow](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/workflow-build-semantic-model.html)
- [Physical diagram and joins](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/open-physical-diagram-physical-layer.html)
- [Logical business models](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/create-business-model-logical-layer.html)
- [Presentation subject areas](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/create-subject-area.html)
- [AI logical column names](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/automatically-rename-logical-columns.html)
- [AI presentation table descriptions](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/generate-presentation-table-description.html)
- [AI presentation column descriptions](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/generate-presentation-column-description.html)
- [Import an archived model](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/import-_zip-file-create-semantic-model.html)

## Narratives

- [Language Narrative supported data shapes and limitations](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/language-narrative-visualization.html)
- [Oracle narrative hands-on tutorial](https://docs.oracle.com/en/cloud/paas/analytics-cloud/tutorial-add-language-narrative-visualization/)

## Existing MPHA material reused

- Existing local MPHA workshop README and data dictionary establish the synthetic scenario and claims star grain.
- Existing MPHA workshop Git remote: [public-healthcare-AIDP-workshop](https://github.com/Jayaramu24/public-healthcare-AIDP-workshop).
- Live OAC dataset, source catalog queries, workbook values, data flow run history, and downloaded output CSV establish the numerical checkpoints. These are tenant observations, not facts inferred from product documentation.

## Industry Analytics semantic demo — verified 20 October 2026

- [Inspect physical source data](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/inspect-data-physical-tables.html) — Preview is sampled; it is not an acceptance aggregate query.
- [Automatically rename logical columns](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/automatically-rename-logical-columns.html) — live Suggest Names path verified.
- [Generate presentation column description](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/generate-presentation-column-description.html) — live Detail view generation verified.
- [Work with presentation tables and columns](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acmdg/work-presentation-tables-columns.html) — presentation metadata and descriptions.

The runbook separates official documented behavior from actual tenant outcomes. Industry model save/reopen and AI actions are verified; deployed queries and full P01 control totals are not.


## OAC MCP, Claude and iframe exercise — researched and verified 20 October 2026

- [OAC MCP preview](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/access-oracle-analytics-cloud-mcp-server-preview.html)
- [Official local MCP utility](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/oac-mcp-connect-preview.html)
- [Available MCP tools](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/available-oracle-analytics-cloud-mcp-tools-preview.html)
- [Visible tool metadata](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/visible-mcp-tool-metadata-preview.html)
- [Catalog discovery](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/catalog-discovery-preview.html)
- [Workbook save contract, approval and local jsonPath](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/save-catalog-content-preview.html)
- [MCP safety rules](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/safety-rules-preview.html)
- [MCP troubleshooting](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/troubleshooting-preview.html)
- [Inline HTML in an OAC iframe](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/use-iframe-visualization-embed-html-canvas.html)
- [External iframe options and sandbox controls](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/embedding-external-content-workbook-canvas.html)
- [Claude local MCP server setup](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Claude remote connector setup](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) — separate from the local Desktop bridge tested here.
- [Oracle Logical SQL aggregation and BY syntax](https://docs.oracle.com/middleware/12213/biee/BIESQ/toc.htm)

The local utility’s downloaded README and tool metadata describe content.jsonPath as a local shortcut expanded into canonical content.json. Actual Claude serialization exposed a string/object boundary issue; the workshop compatibility helper and its write restrictions are documented as local workshop code. The JSON structure, plugin IDs and projectVersion were inspected in this tenant’s actual saved workbooks. Visual similarity is an implementation result, not a documented automatic HTML-to-native conversion feature.
