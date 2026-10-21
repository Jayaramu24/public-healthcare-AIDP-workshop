# Industry Analytics instructor demonstration

Updated 20 October 2026. Only Lab 7 uses Industry Analytics. The other seven feature labs remain hands-on in the original workshop OAC environment. The total agenda remains 180 minutes; Lab 7 remains 15 minutes.

The private model **MPHA_Claims_Semantic_Demo** is prepared and reopened successfully. Use [Lab 7](labs/lab-07-semantic.md) for the screenshot-backed live script and full preparation steps.

## Verified evidence

- Existing System connection `semmodel` exposes `ORIGAMI_P01`.
- Physical database `MPHA_AILH` contains the monthly claims fact and four dimensions with four explicit many-to-one inner joins.
- Business model `MPHA Claims` contains five logical tables; dimension primary keys came from imported metadata.
- Seven counts and amounts use SUM. `Claims Denial Ratio` is a validated post-aggregate logical expression with a zero-denominator guard.
- Presentation subject area `MPHA Claims Workshop Demo` has five folders. `Claims Metrics` contains exactly eight reporting measures; fact keys and the two stored segment statistics are excluded from that presentation folder.
- Semantic Modeler Assistant generated fact-column names; seven reviewed renames were applied and saved. It also generated a repeatable dimension-naming preview.
- Assistant table and column descriptions were generated, reviewed and saved. The final descriptions were verified after reopening the completed model.
- All-object consistency with warnings included completed with **0 errors, 0 warnings and 0 hidden warnings**.
- Physical fact Preview returned sampled live data through `semmodel`.
- The archive was downloaded and its exported JSON inspected. It contains connection references, metadata and expressions; no credential fields were found. The extracted source is included in this package.

![Completed model reopened](images/industry-semantic/19-completed-model-reopened.jpg)

![Clean consistency result](images/industry-semantic/15-consistency-zero-errors.jpg)

## Repeatable presenter state

Claim Classification deliberately retains `CLAIM_TYPE`, `SERVICE_CATEGORY`, `DIAGNOSIS_GROUP` and `CLAIM_TYPE_KEY`. Generate suggestions, reject the key rename and cancel the preview. This permits repeated demonstrations without resetting the prepared starter. Show the fact naming screenshot as the verified Apply example.

If demonstrating Apply live, import a separate private copy, apply only the three business names and save. Review presentation mappings after refactoring. Restore the approved table and column description text from Lab 7 after each generation demonstration.

Use [the archive builder](scripts/build_model_archive.py) to create a local ZIP from the exported source. Import it as a new model; never select Import Deployed Model or Deploy for this exercise. Archive export and source inspection were tested; round-trip import was not rehearsed.

## Limits that must remain explicit

This model is **private and undeployed**. Metadata consistency does not establish runtime query correctness, row-level security or user permissions. No shared Industry Analytics semantic runtime was replaced.

The source Preview is sampled. Full P01 totals and dimension completeness remain unverified. The original ClaimStar_KJ baseline of 1,400 claims belongs to ORIGAMI_ADMIN02 and must not be presented as a verified P01 control total. If expanding to runtime analytics, run [the acceptance SELECTs](sql/ORIGAMI_P01_ReadOnly_Acceptance.sql) and use the environment owner's approved test-deployment process.

Weighted duration remains available in the original hands-on workbook/data-flow labs; it is not part of this semantic starter's reporting measures. No hierarchies, row-level security policy or deployed subject-area query test were added to this 15-minute metadata demonstration.

See [the machine-readable verification record](checkpoints/semantic-model-verification.json). The successful 20 October rehearsal is included as the final optional instructor demonstration. This verification record describes that private, undeployed model.
