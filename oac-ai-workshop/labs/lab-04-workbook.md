# Exercise 5: compare Workbook Assistant with discovery

10 minutes · Verified 19 October: generated chart, add to canvas, save and post-index retest

You will ask a concrete business question, inspect the generated chart and explanation, and add the chart to your canvas. The rehearsal base returned district volumes that reconcile to 1,400 claims.

## Task 1 Open Assistant

1. Continue in Claims_AI_Pxx, created from the released, indexed ClaimStar_WS_Base. Create a blank canvas for the district workload question.
2. Open the Auto Insights drawer and choose Assistant. Wait for the dataset availability/index check. Use the existing prepared source used in the successful screenshots.
3. Enter the business prompt below. Compare the response with the chart candidates shown by Auto Insights. This demonstrates prompted analysis after automated chart discovery.
4. These generation and post-index retest screenshots were captured in the successful 19 October rehearsal. If the live service is unavailable, continue from the saved generated chart in MPHA_Claims_AI_Workshop_Seed, using Save As to your own workbook.

![New workbook created from the isolated dataset.](../images/20-new-workbook.jpg)

![Assistant panel ready for a typed question.](../images/21-workbook-assistant-ready.jpg)

## Task 2 Generate and verify the chart

```text
Create a bar chart of Claims Submitted by District Name.
```

1. Paste the prompt in the Assistant input and press Enter. Wait until the chart and explanatory text have both appeared.
2. Confirm it uses the count Claims Submitted, summed by District Name. A row count would count 622 segments and answer a different question.
3. Check the district values against the table below. Check that all five districts are present.
4. Review the prose separately from the chart. Terms such as outlier are Assistant interpretations and should not be treated as a demonstrated statistical test.

![Actual generated district claims chart and explanation.](../images/22-assistant-generated-chart.jpg)

| District | Claims Submitted | Share |
| --- | --- | --- |
| Central City | 413 | 29.50% |
| East River | 287 | 20.50% |
| North Borough | 255 | 18.21% |
| South Lakes | 264 | 18.86% |
| West Hills | 181 | 12.93% |
| Total | 1,400 | 100% |

## Task 3 Add the visualization and save

1. Hover over the generated chart to reveal its chart toolbar. Click Add to Canvas on that toolbar.
2. Do not confuse Add to Canvas with the Add suggestion button below the response. That button helps compose a follow-up prompt; it does not place the chart on the canvas.
3. Close the Assistant drawer and confirm the chart is on the new district-claims canvas.
4. Save the workbook as Claims_AI_Pxx in your own folder. Check the workbook title after saving.

![Generated chart action used to add the visualization to the canvas.](../images/23-add-assistant-chart-to-canvas.jpg)

![The chart on the workbook canvas before the calculation and narrative labs.](../images/24-chart-on-canvas.jpg)

## Checkpoint

Claims_AI_Pxx contains a five-district chart with a total of 1,400 claims. Recovery: open MPHA_Claims_AI_Workshop_Seed and use Save As with your participant name.

> If Assistant generation is unavailable, select Claims Submitted and District Name in Data Elements, then right-click → Create Best Visualization. Choose Bar if necessary. Confirm 413 / 287 / 255 / 264 / 181 and total 1,400. Keep just one district-claims bar for the following drill/explanation exercise.

In the successful 19 October run, this prompt also returned after reviewed metadata was saved and the index refreshed. The screenshot below records that separate post-index test; it is not a claim of a new 22 October response.

![Successful district chart response after the final metadata refresh, with the saved workbook visible behind the drawer.](../images/57-assistant-after-metadata-refresh.jpg)

[Oracle documentation for Workbook Assistant](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/generate-visualizations-workbooks-oracle-analytics-ai-assistant.html)
