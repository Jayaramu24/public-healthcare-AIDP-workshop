# Exercise 2: generate and review catalog descriptions

5 minutes · Verified 19 October: prepared-base generation and persistence

A catalog description helps another analyst discover the correct dataset without opening it. This is separate from the field-level AI descriptions in Lab 3.

> Use the prepared-base route shown in this successful rehearsal. In Home → Data, find the released ClaimStar_WS_Base. Choose Actions → Duplicate and save your own copy as Claims_AI_Base_Pxx in My Folders. This contains the same flattened claims data plus Processing Days Total Approx. Keep MPHA_Claims_Pxx, your new 19-field dataset, as the connection/preparation result. Change only your own metadata copy.

## Task 1 Generate the description

1. Return to Home. On your Claims_AI_Base_Pxx dataset, select Actions, then Inspect.
2. On General, locate Description and click the wand beside it. Wait for generation to finish; the field may be briefly empty.
3. Read the generated text. Keep a clear statement of monthly claims activity, district and program dimensions, and supported analyses. Remove unsupported claims about patient-level detail, currencies, clinical causation, or real-time data.
4. Click Save. Close and reopen Inspect to confirm the description persisted.

![General inspector for the isolated workshop base before description generation.](../images/10-catalog-description-before.jpg)

![Actual generated description on the base copy; it was saved during preparation.](../images/11-catalog-ai-description-result.jpg)

## Checkpoint

Your dataset has a concise catalog description. The source ClaimStar_KJ remains unchanged. The generated text should describe contents and analytical use, not infer a cause of claim denials.

[Oracle documentation for catalog metadata generation](https://docs.oracle.com/en/cloud/paas/analytics-cloud/acubi/add-metadata-dataset-using-ai.html)

> The screenshots show the successful prepared-base run from 19 October. If the live AI service is unavailable, review the saved generated description and explain the edits; proceed with the existing prepared text. Fresh-source generation is not a required exercise.
