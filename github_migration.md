# GitHub Migration

Use this note when you want to move the workshop kit into your own GitHub location.

## Recommended approach

Treat `public_healthcare_lakehouse_workshop/` as the repository root so the HTML page, PDF guide, data samples, SQL, and notebooks stay together.

## Basic push flow

1. Open a terminal in the workshop folder:

```bash
cd /Users/jayarkri/Documents/Codex/2026-06-08/https-livelabs-oracle-com-ords-r/outputs/public_healthcare_lakehouse_workshop
```

2. Initialize Git and commit the package:

```bash
git init
git add .
git commit -m "Initial public healthcare lakehouse workshop kit"
git branch -M main
```

3. Create an empty GitHub repository in your account or organization.

4. Connect the local folder to your GitHub repository and push:

```bash
git remote add origin https://github.com/<your-org-or-user>/<your-repo>.git
git push -u origin main
```

## If you already have a GitHub repository

Copy the `public_healthcare_lakehouse_workshop/` folder into that repository, commit it as a subfolder, and push as usual.

## Suggested structure to keep in GitHub

- Keep `index.html`, `workshop_guide.md`, and `workshop_guide.pdf` in the repo so reviewers can browse or download the workshop directly.
- Keep `data/`, `documents/`, `sql/`, `notebooks/`, and `optional_labs/` together so facilitators can run the workshop without hunting for dependencies.
- Keep `outputs/public_healthcare_lakehouse_workshop.zip` outside the repo if you only use it as a packaging artifact. Commit it only if your execution team wants a single downloadable bundle stored in GitHub.

## Notebook sequence after migration

Use the Spark notebooks in this order:

1. `notebooks/aidp_bronze_pyspark.py`
2. `notebooks/aidp_silver_pyspark.py`
3. `notebooks/aidp_gold_pyspark.py`

The older `notebooks/aidp_refinement_pyspark.py` file remains only as a legacy all-in-one reference.
