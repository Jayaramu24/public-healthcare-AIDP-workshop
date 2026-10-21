# Launch: claims contract and participant setup

10 minutes · Required

In this three-hour workshop, experienced analysts use Oracle Analytics Cloud AI features to investigate MPHA healthcare claims. You will prepare metadata, build and validate visualizations, create a rollup data flow, compare narratives with the numbers that support them, and use Claude MCP to discover data and build an HTML overview with a native OAC recreation. MPHA is the synthetic healthcare scenario in the existing workshop kit.

> Revised 22 October 2026. AILH connectivity is already available. Begin with the flattened MPHA_OAC_STAR_CLAIMS view; do not configure a wallet or rebuild joins in the core workshop. Auto Insights and column Explain precede Workbook Assistant. Forecast, Explain Selected and drill follow the first saved workbook. Dimensional modelling is optional DIY; Semantic Modeler is an optional instructor demo at the very end.

> Evidence comes from successful rehearsals on 19–22 October 2026. Earlier successful AI features are retained with their original screenshots and source names. The fresh 19-field dataset teaches connection and preparation. For Auto Insights use the already discovered ClaimStar_WS_Base; for metadata changes use your own copy of that prepared base. Both read the same flattened claims view.

## Objectives

- Create an individual 19-field dataset from the existing AILH connection and flattened view.
- Discover suitable charts using Auto Insights, then compare the Workbook Assistant approach.
- Explain a category, investigate a selected district, drill and forecast. Validate every result against the data contract.
- Create a district-month rollup and compare HTML with native OAC dashboards created through MCP.

## Task 1 Sign in and establish your participant identity

1. Sign in to the facilitator-assigned OAC using your own author account. Keep the workshop open in another Chrome tab.
2. Use your assigned P01–P20 ID. Create MPHA_Claims_Pxx and Claims_AI_Pxx in your own My Folders. Screenshots use the instructor’s MPHA_OAC_Star_Claims_WS and MPHA_OAC_Analytics_Demo.
3. Confirm the pre-existing MaxicareWorkshop AILH connection is visible, with permission to read ORIGAMI_ADMIN02.MPHA_OAC_STAR_CLAIMS. Your administrator supplies the equivalent connection/schema if names differ.
4. The facilitator also releases ClaimStar_WS_Base and prepared workbook/flow seeds before class. That older base uses the same flattened view plus one approximate processing numerator (20 fields); the fresh participant source has 19 fields. Use that prepared base only where explicitly requested.

![Existing MaxicareWorkshop connection: choose the flattened MPHA_OAC_STAR_CLAIMS view. The dimension and fact tables are reserved for optional DIY.](../images/revised/01-flattened-source.jpg)

## Task 2 Check the data contract

| Item | Expected |
| --- | --- |
| Dataset grain | One monthly district × coverage program × claim classification segment |
| Source rows | 622 segments |
| Period | January through June 2025; Service Month uses month-start dates |
| Claims submitted / approved / denied / pending | 1,400 / 1,214 / 121 / 65 |
| Paid total | 896,370.39; do not invent a currency label |
| Overall denial rate | 121 ÷ 1,400 = 8.642857…%, displayed as 8.64% |
| Weighted processing days | 19,025.2 ÷ 1,400 = 13.589428… days, displayed as approximately 13.59 |
| Output rollup grain | 30 district-month rows; six months × five districts |

> Each row is an aggregated segment, not an individual claim. Sum claim counts and amounts. Never sum Denial Rate or Average Processing Days. The prepared 20-field rollup base has an approximate numerator reconstructed from rounded means; the new 19-field participant source does not contain that helper.

## Task 3 Use Zoom checkpoints

1. Keep your microphone muted while working and paste prompts from this guide. Use chat for your participant ID and short status messages.
2. When the facilitator calls a checkpoint, post Pxx green when complete, Pxx amber with the exact blocker when stuck, or Pxx recovered when you used the fallback.
3. Do not share credentials in chat. If you fall behind for more than two minutes, open the prepared seed and rejoin at the next task.
