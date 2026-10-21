# Claude Free + OAC MCP exercise files

Use [Lab 9](../labs/lab-09-mcp-claude.md) for the timed walkthrough. These files support a presenter demonstration and optional preconfigured participants. Configure clients before the Zoom session.

## Rehearsal artifacts

- [Reviewed executive HTML](MPHA_Executive_Overview.html): self-contained, dated 30-row synthetic snapshot; no external hosting or runtime assets.
- [HTML iframe workbook](MPHA_MCP_Executive_HTML.workbook.json): actual OAC workbook JSON with an SRCDOC iframe containing the reviewed HTML.
- [Native workbook](MPHA_MCP_Executive_Native.workbook.json): performance tiles, line, horizontal bar, table and text boxes mapped from the HTML design.
- [Design mapping](design-mapping.json), [data snapshot](claims-mcp-snapshot.json), and [live verification](verification.json).

The native JSON is tenant-specific, projectVersion 1168, and references ClaimStar_WS_Base. It is a workbook definition, not a JSON rendering of arbitrary HTML. Use an actual saved template from the destination OAC release when adapting it. The HTML is a static snapshot; native visuals query the accessible OAC dataset. This account’s native paid values use Indian digit grouping; the HTML uses US digit grouping. The numeric amounts are equal, and no currency is implied.

## Pre-work setup

1. In your OAC profile open Developer Options → MCP Connect. Download and extract the official utility **with its lib directory**. Oracle software is not redistributed here.
2. Install Node.js 18.17+ and Claude Desktop through your approved software process. Find the absolute Node path with `which node` (Windows: `where node`). The tested account is Claude Desktop Free; no API key or paid subscription was used. Availability and Free limits may change.
3. Copy [oracle-bridge.example.json](oracle-bridge.example.json) to `oracle-bridge.json` locally. Replace the OAC base URL, private state directory and permitted workbook folder with your actual values. Begin with read-only tools; add the save tool for the explicitly approved exercise. The example includes it to show the final tested setup. Do not enable all write tools.
4. Copy [compat-config.example.json](compat-config.example.json) to `compat-config.json`. Set the paths to Node, the unchanged Oracle utility and your bridge config. Create or locate your assigned private folder in OAC Catalog → My Folders. In Claude’s discovery request, search_catalog type folders, search the exact folder name, limit 5. Check owner/path and use its returned id as parentId. Set that actual private folder ID and exactly two unique workbook names. Leave replaceIds empty for create-only operation.
5. In Claude → Settings → Developer → Edit config, merge the server entry from [claude-desktop.example.json](claude-desktop.example.json) into your existing configuration. Preserve unrelated entries. Set the actual absolute paths. Do not add credentials to this file.
6. Quit and reopen Claude. Complete the Oracle browser sign-in using your own OAC credentials. The connector inherits that account’s OAC access; the OAuth scope seen in rehearsal was consumer::all. Approve the intended account and only synthetic aggregate results for this exercise. Authentication state stays in the private directory and must not go to Git.
7. Confirm Developer → oac-mcp-connect → Running. Run the short discovery prompt before the workshop. The local stdio route was tested; a Claude remote custom connector is a different configuration and is not the runbook’s tested path.

## Why the compatibility helper is supplied

The actual Claude/OAC rehearsal initially passed `content` as stringified JSON. Oracle’s utility forwarded it without expanding `jsonPath`, and OAC returned INVALID_INPUT: workbook content must include json. The supplied [claude-oac-compat.cjs](claude-oac-compat.cjs) runs locally in Node, normalizes stringified content to an object, constrains the advertised content schema, then forwards stdio messages to Oracle’s unchanged utility. It also rejects saves outside the configured workbook type, exact create names/private parentId, or separately approved replacement IDs. It does not read browser tokens or contact OAC itself.

The current presenter configuration using this logic was verified Running and both creates succeeded through Claude. The portable example paths must be adapted and rehearsed on each participant machine. This compatibility helper is workshop source code, not an Oracle-supported product feature.

## Adapting data and repeating the lab

- In this tenant the presenter uses ClaimStar_WS_Base. Participants may use that approved released dataset if it is accessible to them. A private workbook does not itself grant dataset access.
- For a participant’s dataset copy, discover its actual XSA object reference. Replace every occurrence of the original namespace/name in criteria, datasource metadata and filters; do not change only a display label or UUID substring. Validate with one query and a saved template in that account before the event. The supplied JSON should not be treated as cross-tenant portable without this work.
- The original source has 622 monthly district × program × claim-type segments, Jan–Jun 2025. Counts and paid amount are additive. Overall rates divide total counts. District table formulas explicitly aggregate BY District Name. Reusing the overall tile formula in every table row initially repeated the overall rate; this was caught in live validation and corrected in the delivered native JSON.
- Use new Pxx names on each replay. Catalog name collisions stop the prompt; do not approve an overwrite of the presenter reference. If a private demo copy needs refinement, approve that exact existing ID before adding it to replaceIds.
- Reuse the prepared JSON and `content.jsonPath`; do not dump 70KB of workbook JSON into Claude. Oracle’s local bridge reads the file and sends canonical content.json. Place files inside allowedFileRoots.

## Minimal request budget and recovery

Aim for three task requests: catalog discovery; one metadata + bounded query + HTML artifact; exact approved workbook saves. The preparation used two extra small save attempts to isolate the serialization issue and a fresh final save conversation; local fixes and verification did not consume additional Claude requests. No API usage or paid upgrade was purchased.

If Claude quota is exhausted, compare the supplied HTML and saved native OAC workbook, validate metrics, and use the documented manual iframe steps. If a save reports success without an ID/URL, perform one exact-name catalog search and use its returned viewUrl; do not invent an artifact URL. If validation fails, stop and inspect the template and dataset references. Do not repeatedly regenerate the dashboard or silently deduplicate query rows.

[Offline compatibility-helper checks](compatibility-checks.json) exercise normalization and write rejection without contacting OAC.
