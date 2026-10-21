# Lab 9 Create executive dashboards with Claude and OAC MCP

**Time:** 30 minutes  |  **Rehearsal status:** Verified · Claude Free + two saved OAC workbooks

Follow the complete sequence: discover a dataset through MCP, query bounded claims aggregates, create an HTML executive overview, embed it in an OAC iframe, and recreate its design as native OAC visuals using workbook JSON. The HTML is the visual reference. The native workbook remains connected to OAC data; the HTML contains a dated snapshot.

> Delivery: presenter demonstrates Claude Desktop Free; participants with an approved, preconfigured client may follow using their own accounts and private names. Everyone validates the HTML and native workbook side by side. Install and authenticate before the meeting. Do not spend this 30-minute slot configuring 20 laptops or share the presenter’s Claude/OAC login. Semantic Modeler remains the separate instructor-only demo in Lab 7.

## Exercise files

[MCP setup and compatibility helper instructions](../mcp/README.md)

[Reviewed HTML executive overview](../mcp/MPHA_Executive_Overview.html)

[HTML iframe workbook JSON](../mcp/MPHA_MCP_Executive_HTML.workbook.json)

[Native OAC workbook JSON](../mcp/MPHA_MCP_Executive_Native.workbook.json)

[Design mapping and saved-object verification](../mcp/verification.json)

## Before the workshop: connect once, outside the timebox

1. Sign in to the original workshop OAC. Open your profile menu → Profile → Developer Options → MCP Connect. Download the utility from this instance. Extract the whole oac-mcp-connect folder, including lib. Do not copy just its JavaScript entry point.
2. Install Node.js 18.17 or later through your approved software process and install Claude Desktop. In Claude → Settings → Developer → Edit config, register the local stdio bridge for your OAC base URL. Use the configuration examples in mcp/README.md. No Claude API key is required for the tested desktop route.
3. Restart Claude. When Oracle opens a browser for authentication, sign in with your own OAC account and complete the callback. The connector acts with that user’s OAC permissions; a Claude account does not grant OAC access.
4. In OAC Catalog → My Folders, create your private MPHA_AI_Pxx folder if the facilitator has not assigned one. Use catalog search type folders with that exact name to retrieve its ID; confirm the owner and path. For the presenter, reuse MPHA_AI_Workshop. Never infer a parentId from a display name.
5. Verify Developer shows Running. Begin with the five read-only discovery/query tools. Enable the experimental workbook save tool only for the approved exercise and exact private destination. Keep auth state, logs, wallets and passwords out of the package and Git.
6. Rehearsal exposed a payload issue: Claude serialized content as a string before Oracle’s jsonPath shortcut ran. The supplied local compatibility helper normalizes that field, restricts save targets and forwards to the unchanged Oracle utility. Rehearse this path before class. This is workshop code, not an Oracle product component.

![Claude Desktop Free account used in the live rehearsal. Plan limits can change; no paid upgrade or API key was used.](../images/claude-mcp/01-claude-free.jpg)

*Claude Desktop Free account used in the live rehearsal. Plan limits can change; no paid upgrade or API key was used.*

![Actual Origami OAC profile Developer Options and MCP Connect setup at 1920 × 1080.](../images/claude-mcp/04-oac-mcp-connect.jpg)

*Actual Origami OAC profile Developer Options and MCP Connect setup at 1920 × 1080.*

![Verified Running status after the local compatibility helper was configured. This native desktop capture is 2400 × 1600.](../images/claude-mcp/09-claude-compat-running.jpg)

*Verified Running status after the local compatibility helper was configured. This native desktop capture is 2400 × 1600.*

## Task 1 Discover the relevant data — minutes 0–4

Presenter: open a new Claude conversation. Participants use their own client only if pre-work passed. Approve individual tool calls with Allow once after checking the requested tool and scope.

```text
Use only oac-mcp-connect. Read-only. Search the catalog for ClaimStar datasets, limit 5. Return names and IDs in a compact table. Identify the dataset suited to monthly district healthcare claims. Also search my assigned private folder by its exact name, type folders, limit 5; return its path and parent ID after checking its owner. Do not query data or create anything. Reply under 160 words.
```

1. Expand OA:Catalog Search and inspect the request and response. The rehearsal found ClaimStar_KJ and the prepared ClaimStar_WS_Base.
2. Use ClaimStar_WS_Base for the shared presenter reference. Record the actual dataset ID; do not invent it from its display name. Participants using ClaimStar_Pxx must discover their own ID and check access.
3. Explain that discovery found catalog objects. It did not validate metrics or grant permission. Natural-language source matching is a separate available tool and was unnecessary in this successful catalog search.

![Actual Claude MCP catalog discovery found the two relevant claims datasets.](../images/claude-mcp/03-dataset-discovery.jpg)

*Actual Claude MCP catalog discovery found the two relevant claims datasets.*

## Task 2 Query once and generate the HTML first — minutes 4–10

```text
Use only ClaimStar_WS_Base. Read-only. Inspect MPHA_OAC_STAR_CLAIMS metadata once. Query Jan–Jun 2025 grouped by Service Month and District Name: SUM Claims Submitted, Approved Claims, Denied Claims, Pending Claims, Total Paid Amount, and Processing Days Total Approx. Use fully qualified Logical SQL, order by month and district, maxRows 40 and FETCH FIRST 40 ROWS ONLY. Do not silently deduplicate. Check for 30 unique month-district rows and totals: 1400 submitted, 1214 approved, 121 denied, 65 pending, 896370.39 paid. Then create one self-contained HTML artifact under 12KB: warm ivory, navy headings, teal submitted and coral denied; four KPI cards, monthly submitted line, district denied bars, district summary table, and district selector that filters everything. Ratios must divide aggregate sums with zero protection. Weighted days = summed processing numerator / submitted, labelled approximate. Paid currency unspecified. Label synthetic data, Jan–Jun 2025, snapshot date. No external scripts/assets or OAC writes. Reply under 80 words.
```

1. Inspect the metadata and Logical SQL calls. The tested query returned 30 rows without deduplication. If extra rows or duplicate grains occur, stop and investigate the query rather than deleting records.
2. Open the generated artifact. Save it as MPHA_Executive_Overview.html in your local mcp folder. Inspect its HTML and data before embedding. The supplied reviewed version reconciles every row to the downloaded OAC rollup CSV.
3. Confirm the four default cards: 1,400 submitted, 86.71% approval, 8.64% denial, 896,370.39 paid. Select Central City: 413, 84.75%, 10.17%, 252,227.62. Check the line, bars and table all change.
4. Explain the review corrections made after generation: consistent two-decimal formatting, a weighted approximate duration, complete selector behavior and a visible snapshot label. Native amounts follow the account locale; US 896,370.39 and Indian 8,96,370.39 denote the same value. A generated artifact is a draft until checked.

![The original HTML artifact generated by Claude after its bounded MCP query. Local review refined the delivered version without repeated Claude requests.](../images/claude-mcp/08-claude-generated-html.jpg)

*The original HTML artifact generated by Claude after its bounded MCP query. Local review refined the delivered version without repeated Claude requests.*

![Reviewed HTML executive overview used as the visual reference for the native workbook.](../images/claude-mcp/05-html-executive-overview.jpg)

*Reviewed HTML executive overview used as the visual reference for the native workbook.*

![Central City selection in the reviewed HTML: all visual components and KPI cards respond.](../images/claude-mcp/06-html-district-filter.jpg)

*Central City selection in the reviewed HTML: all visual components and KPI cards respond.*

## Task 3 Embed the reviewed HTML in OAC — minutes 10–16

1. Review the exact new workbook name and private destination before approving save. The presenter approved MPHA_MCP_Executive_HTML and MPHA_MCP_Executive_Native in My Folders / MPHA_AI_Workshop. Participants use unique Pxx names in their own private folder.
2. For the reproducible MCP path, use the supplied MPHA_MCP_Executive_HTML.workbook.json, which contains one native iframe visualization with sourceType SRCDOC and the reviewed HTML in frameSrc. The JSON was built from the tenant’s actual saved workbook structure.
3. Use the compact save prompt below after replacing both absolute file paths and the actual discovered parentId. content must be an object, with jsonPath local to the bridge process. Do not paste thousands of JSON lines into Claude.
4. Open the returned HTML workbook URL in OAC. Verify its heading, snapshot label and district selector. This embeds inline HTML without external hosting. The JavaScript runs in the iframe’s configured sandbox; leave Forms and Same Origin at their defaults.
5. Show the manual path as the recovery: new workbook → Visualizations gallery → iframe → Properties → SRC → SRCDOC → paste the reviewed HTML → Save As under your private name. Do not paste HTML into a URL field. The native JSON file below is a workbook definition, not a general-purpose HTML-to-JSON conversion.

![The actual OAC visualization gallery exposes iframe. SRCDOC accepts the reviewed self-contained HTML.](../images/claude-mcp/07-oac-iframe-gallery.jpg)

*The actual OAC visualization gallery exposes iframe. SRCDOC accepts the reviewed self-contained HTML.*

```text
I approve creating ONLY <HTML_NAME> and <NATIVE_NAME> as new private workbooks under parentId <ACTUAL_PRIVATE_FOLDER_ID>. Use OAC MCP. Search both exact names first; stop if either exists. Save type workbooks, userApproved true. For <HTML_NAME>, content must be an object: {"jsonPath":"/ABSOLUTE/mcp/MPHA_MCP_Executive_HTML.workbook.json"}. For <NATIVE_NAME>, use {"jsonPath":"/ABSOLUTE/mcp/MPHA_MCP_Executive_Native.workbook.json"}. Do not read or rewrite file contents in chat. No other writes or permissions changes. Stop on error; return statuses, IDs and URLs under 100 words.
```

![Actual Claude MCP save results: both private workbooks created successfully, status ok (200).](../images/claude-mcp/10-claude-two-workbooks-saved.jpg)

*Actual Claude MCP save results: both private workbooks created successfully, status ok (200).*

![Saved HTML workbook opened in OAC: the reviewed HTML renders inside its iframe.](../images/claude-mcp/11-oac-iframe-dashboard.jpg)

*Saved HTML workbook opened in OAC: the reviewed HTML renders inside its iframe.*

![Central City inside the OAC iframe: 413 submitted, 84.75% approved, 10.17% denied and 252,227.62 paid.](../images/claude-mcp/12-oac-iframe-filter.jpg)

*Central City inside the OAC iframe: 413 submitted, 84.75% approved, 10.17% denied and 252,227.62 paid.*

## Task 4 Recreate the design as native OAC visuals — minutes 16–25

1. Keep the HTML open as the reference. Compare its palette, title hierarchy, four-card row, two-chart row and district table with the native workbook definition. Use mcp/design-mapping.json to see each mapping.
2. Inspect the prepared native JSON locally. It reuses a saved OAC template and the tenant’s projectVersion 1168. It defines real OAC performance tiles, a line chart, horizontal bar, table and text boxes; it does not put the HTML inside each chart.
3. After the approved MCP save completes, open MPHA_MCP_Executive_Native. Verify all four KPI values against the HTML and verify the six-month scope. The native date predicate is Jan 1 inclusive through Jul 1 exclusive, 2025. The district table uses separate explicit BY District Name ratio expressions: the first live check caught and corrected overall ratios repeated down district rows.
4. Use the OAC District filter and select Central City. Confirm all four cards and both charts update, and the table reduces to Central City. Clear the filter and return to all districts. The HTML uses its internal selector; OAC uses the native filter bar.
5. Save, close and reopen the native workbook to confirm persistence. Preserve the presenter reference. Participants create a uniquely named copy; an MCP replacement by id requires approval for that exact existing target.

| HTML reference | Native recreation | Expected difference |
| --- | --- | --- |
| Four rounded KPI cards | Four OAC performance tiles | OAC formats and font metrics may differ |
| Monthly SVG line | OAC line chart | Native axes, tooltips and chart padding |
| District SVG bars | OAC horizontal bar | Native category and value labels |
| HTML district table | OAC native table | Native headers, scrolling and number formats |
| HTML district selector | OAC filter bar | Different control position; same filter scope |
| Embedded 30-row snapshot | OAC dataset queries | Native evaluates current accessible data; HTML refresh requires a new snapshot |

![Reopened native OAC workbook after validation: four tiles, two charts and the corrected district summary match the HTML reference.](../images/claude-mcp/13-oac-native-dashboard.jpg)

*Reopened native OAC workbook after validation: four tiles, two charts and the corrected district summary match the HTML reference.*

![Native OAC District filter: select Central City, then click outside the popup to apply. Clear selections to restore all districts.](../images/claude-mcp/15-oac-native-filter-dialog.jpg)

*Native OAC District filter: select Central City, then click outside the popup to apply. Clear selections to restore all districts.*

![Native Central City result matches the iframe. OAC displays paid as 2,52,227.62 under this account locale; the amount equals 252,227.62.](../images/claude-mcp/14-oac-native-filter.jpg)

*Native Central City result matches the iframe. OAC displays paid as 2,52,227.62 under this account locale; the amount equals 252,227.62.*

## Task 5 Validate and explain — minutes 25–30

1. Compare all-district totals and Central City values in both workbooks. Count six points on the monthly trend and five districts in the summary. Explain why aggregate approval and denial ratios are recomputed rather than averaged.
2. Distinguish a screenshot from a working result: expand the actual MCP save response, open each returned object and interact with its filter.
3. Explain the boundary: visual similarity is achieved by mapping design elements to supported OAC visuals. Arbitrary HTML/CSS does not automatically become a native OAC dashboard. The native JSON must match a valid workbook template and dataset identifiers.
4. Participants post Pxx MCP validated plus one difference between snapshot HTML and a native workbook. The cohost records anyone using the prepared artifacts because their client was unconfigured or Claude Free quota was exhausted.

> Quota plan: use one catalog request, one bounded query/artifact request, and one approved save request. Reuse the reviewed files. Do not repeatedly resend metadata, dump workbook JSON into chat, or let every attendee debug a different layout live. The rehearsal needed small additional save retries to diagnose the content serialization issue; the compatibility helper is included to avoid repeating them. Free-plan limits and service latency are not guaranteed.

[Oracle local MCP utility](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/oac-mcp-connect-preview.html)

[Oracle workbook save contract and local-file shortcut](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acsdv/save-catalog-content-preview.html)

[Oracle iframe SRCDOC instructions](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/use-iframe-visualization-embed-html-canvas.html)

[Claude local MCP setup](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)

[Back to workshop contents](../README.md)
