# README FIRST - MPHA Workshop Execution Pack

Use this pack when preparing or running the Public Healthcare AIDP workshop.

## What to use first

1. Download the workshop execution pack from the Workshop Assets page.
2. Unzip it on your laptop.
3. Upload the notebooks into the assigned AIDP participant folder, for example:

   `E2EAIDPIndustryDemos/Participants/<participant_id>/`

4. Attach the shared Spark compute:

   `E2EAIDPIndustrydemos`

5. Run notebooks in this order:

   - `01_Bronze_Public_Healthcare.ipynb`
   - `02_Silver_Public_Healthcare.ipynb`
   - `03_Gold_Public_Healthcare.ipynb`
   - `04_Claims_Star_AI_Lakehouse_Load.ipynb`

6. Set `participant_id` and, where required, `target_schema` before running.

## SQL scripts

Use the SQL scripts in `sql/` from Autonomous AI Lakehouse Database Actions or the approved SQL execution surface.

Recommended core scripts:

- `admin_prepare_participant_claims_star_schemas.sql`
- `create_ai_lakehouse_claims_star_schema.sql`
- `claims_star_validation.sql`
- `create_ai_lakehouse_claims_context_extension.sql`
- `claims_context_extension_validation.sql`

## Preview links on GitHub

Individual notebook and SQL links on the website are for preview/reference. GitHub may open them as code. For workshop execution, download the ZIP pack and upload the files into AIDP.
