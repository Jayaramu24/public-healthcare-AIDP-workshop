# Exercise 4: Auto Insights and one-click column Explain

25 minutes · Verified 22 October: refreshed gallery, focused settings and saved native chart

Discover candidate charts before writing an Assistant prompt. Auto Insights analyses measures, categories and time to suggest useful views; column Explain profiles the data and proposes relationships. Analysts still decide which question a chart answers.

## Task 1 Open a workbook and inspect Auto Insights

1. Create a new workbook from the released ClaimStar_WS_Base, whose Auto Insights gallery has already been discovered. Keep the source dataset unchanged. Save the workbook as Claims_AI_Pxx in your own My Folders. This avoids waiting for discovery on a fresh dataset during class.
2. Open Auto Insights on the toolbar and select Insights. Expand the drawer to inspect candidate charts. Explain how distributions, category comparisons and time patterns help identify a useful chart before designing the dashboard.
3. Open Insights Settings. Select Claims Submitted, Denied Claims and Total Paid Amount (up to three measures). Select Service Month as the time attribute, and District Name, Coverage Program and Claim Type as small attributes. Turn Generalized Calculations / row-count calculations off and deselect Average Processing Days under Medium Size Attributes.
4. Click Apply and allow the suggestions to refresh. Reopen Settings to confirm the selection persists. A fresh or changed dataset can require background processing; use the pre-discovered source for this exercise.
5. Expand the gallery and find Total Paid Amount Value by Claim Type. Read its explanation and confirm the total 896,370.39. Review suggestions critically: a row count is 622 segments, not 1,400 claims, and a suggested ratio need not be a meaningful business metric.
6. Collapse the expanded drawer. Click Create Canvas (+) to add an empty canvas. Scroll the drawer until the Total Paid Amount Value suggestion is visible, then drag its title/chart onto “Drop your data here to create visualizations”. The drag path was verified in the rehearsal.
7. Close the drawer and inspect the resulting native treemap: Claim Type defines six boxes; Total Paid Amount supplies box size; total 896,370.39. Save. The instructor verification workbook is MPHA_AI_Workshop / MPHA_Auto_Insights_Verification, Canvas 3. Participants keep their own workbook name.

![22 October: refreshed Auto Insights gallery using friendly names and the selected claims measures.](../images/verified/09-auto-insights-refreshed-gallery.jpg)

![Saved focus settings: three measures; Generalized Calculations off; one time attribute; three small attributes; no medium attributes.](../images/verified/10-auto-insights-focus-settings.jpg)

![A regenerated suggestion saved as a real OAC treemap: six claim types, paid total 896,370.39.](../images/verified/11-auto-insight-added-to-canvas.jpg)

> Recovery uses the saved MPHA_Auto_Insights_Verification workbook or the released discovered base. Fresh-source discovery is not in the required path. Auto Insights identifies candidates; the analyst checks aggregation and business meaning.

## Task 2 Explain a low-cardinality column

1. In Data Elements right-click Claim Type and choose Explain Claim Type. This is the column Explain command, separate from chart Explain Selected.
2. Read Basic Facts. The source has six distinct claim types across 622 segment rows. The most common type by segment-row frequency was Outpatient (21%) and least common Inpatient (13%) in rehearsal. These percentages do not describe the 1,400 underlying claims.
3. Open Explain Calculation Settings. Limit related columns to useful business categories and additive measures. Exclude redundant keys/claim classification fields and the stored Denial Rate/Average Processing Days. Apply and review the recomputed facts.
4. Inspect a relationship or segment and ask whether it reflects workload, category definitions or a useful operational hypothesis. Add a useful suggested chart only after checking the measure and grain.

![One-click Explain on the low-cardinality Claim Type source column (raw uppercase names before preparation).](../images/revised/05-explain-column-menu.jpg)

![Explain Basic Facts: six claim types, measured across 622 segment rows.](../images/revised/06-explain-claim-type-facts.jpg)

![Review Explain calculation settings to focus related columns and avoid non-additive sums.](../images/revised/07-explain-relevant-columns.jpg)

Checkpoint: your workbook has one reviewed candidate chart, and you can explain why a 21% category frequency is not automatically a 21% share of claims.

[Oracle: Auto Insights](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/what-are-auto-insights.html)

[Oracle: focus Auto Insights](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/interact-auto-insights-focus-what-youre-interested.html)

[Oracle: Explain quick start](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/quick-start-explain.html)

> Keep one Auto Insights canvas. Create a separate Claims by district canvas for the next exercise, so the Assistant chart and later drill/forecast do not overwrite the discovered treemap.
