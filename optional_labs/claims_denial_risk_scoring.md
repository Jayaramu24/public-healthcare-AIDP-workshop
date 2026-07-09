# Lab 5 - Claims Denial Risk Prediction and MLOps in AIDP

## Goal

Build a predictive claims review-prioritization flow using Oracle AI Data Platform Workbench:

1. Build a Gold-layer ML feature frame at Claims star schema grain.
2. Train a baseline claims denial risk model on historical months.
3. Evaluate the model on a held-out test month before scoring the latest month.
4. Track train, test, and scoring metrics in AIDP Experiments using MLflow.
5. Compare model runs and select the best explainable baseline.
6. Register the selected model in AIDP Models.
7. Batch score the latest claims period.
8. Publish the scored output for OAC and the Claims and Policy Copilot.

## Business use case

MPHA wants to predict which district, coverage program, and claim-type combinations are most likely to show high denial risk in the next review cycle.

Claims operations can use this prediction to prioritize:

- documentation checks
- provider follow-up
- prior-authorization remediation
- policy exception review
- payment leakage investigation
- backlog management

The model does not replace adjudication rules. It creates a ranked review queue so operations teams know where to look first.

## Official Oracle references

Use these official AIDP sources as the reference basis for this lab:

- [AIDP Experiments](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/experiments.html) - experiment creation, MLflow autologging, run comparison, reproducibility, retraining, and model registration from experiment runs.
- [AIDP Models](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/models.html) - model registry, versions, metrics, artifacts, lineage, and batch inference usage.
- [Customer-managed MLflow Servers](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/customer-managed-mlflow-servers.html) - optional pattern for using an external MLflow tracking server from AIDP notebooks.
- [AIDP Quick Start Guide](https://blogs.oracle.com/ai-data-platform/continuing-your-oracle-ai-data-platform-journey-quick-start-guide) - workspace, compute, notebooks, catalogs, and Spark workload setup context.

## Preview feature note

Oracle documents AIDP Experiments and Models as preview capabilities. Confirm availability and compute compatibility in the target tenancy before running this lab live.

Oracle also notes that Experiments and Models are currently not supported on ARM-based compute clusters. Use Intel- or AMD-based compute for this lab.

## Recommended input sources

Use the curated Gold layer as the scoring base:

| Input | Why it matters |
| --- | --- |
| `gold_claims_summary` | Core claims volume, denial, payment, and processing-time signals. |
| `gold_capacity_event_latest` | Operational pressure that can explain delayed adjudication or service strain. |
| `gold_provider_accreditation_summary` | Provider quality and accreditation risk context. |
| `gold_spatial_access_insights` | District pressure, access coverage, and travel context for public-health equity. |

## Feature grain

Keep the model aligned to the Claims star schema grain:

- service month
- district
- coverage program
- claim type

This makes the scored output easy to join back to the Claims star schema and easy to explain in OAC.

## Validated train, test, and score split

The starter notebook uses a time-based split so the model is evaluated before it is used for forward-looking scoring:

| Slice | Months | Current workshop rows | Purpose |
| --- | --- | ---: | --- |
| Train | January 2025 through April 2025 | 410 | Fit the baseline classifier. |
| Test / evaluate | May 2025 | 110 | Calculate held-out evaluation metrics such as `model_auc_test`. |
| Batch score | June 2025 | 102 | Publish the latest operational review queue. |

If the source data is regenerated with fewer months or insufficient label variation, the notebook keeps the lab runnable by falling back to a transparent weighted scoring path and records that condition in the run summary.

## Suggested features

Claims features:

- claims submitted
- approved claims
- pending claims
- total submitted amount
- total paid amount
- payment yield
- average processing days

Operational features:

- supply alert count
- triage total
- occupancy rate
- emergency department wait time
- public-health pressure index

Provider and spatial context:

- accreditation score
- corrective action count
- days to accreditation expiry
- accreditation risk band
- residents per facility
- average travel distance

Target:

- `high_denial_flag`, derived from historical denial rate

## Step-by-step execution

### Step 1 - Confirm prerequisites

Admin confirms:

1. Lab 2 Bronze and Silver notebooks have completed.
2. Lab 3 Claims star schema load has completed.
3. Gold feature sources are available under the workshop Gold-stage path.
4. AIDP Spark compute is Intel- or AMD-based.
5. The participant can open the shared workspace and upload notebooks.
6. The `04_ML` folder exists in the workspace.

Participant confirms:

1. The starter notebook is available: `notebooks/aidp_ml_claims_denial_risk_pyspark.py`.
2. The Gold-stage path is known, for example `oci://mpha-workshop-bucket@<namespace>/mpha/gold_stage`.

![AIDP workspace folders](assets/aidp_ml_lab/screenshots/01_workspace_ml_folder.png)

### Step 2 - Create the AIDP Experiment

In AIDP Workbench:

1. Open **Experiments**.
2. Click **Create**.
3. Name the experiment `MPHA Claims Denial Risk Prediction`.
4. Add a description such as `Tracks model runs for district-program-claim-type denial-risk scoring`.
5. Optionally add tags:
   - `domain=public_healthcare`
   - `model_type=classification`
   - `grain=district_program_claim_type_month`
6. Click **Create**.

Expected result:

The experiment exists and can receive MLflow runs from the notebook.

### Step 3 - Upload and configure the notebook

1. Open the `04_ML` workspace folder.
2. Upload `notebooks/aidp_ml_claims_denial_risk_pyspark.py`.
3. Attach the shared Spark compute.
4. Set:

```python
gold_stage_base = "/Volumes/e2eindustrydemos/default/e2eindustrydemovol/gold_stage"
model_version = "claims_denial_risk_v1"
experiment_name = "MPHA Claims Denial Risk Prediction"
enable_mlflow_tracking = True
```

The notebook is designed to continue in notebook-only mode if MLflow tracking is not available, but the preferred workshop path is to use AIDP Experiments.

![ML notebook uploaded](assets/aidp_ml_lab/screenshots/01b_ml_folder_notebook_uploaded.png)

Checkpoint:

The notebook is attached to compute and shows the validated time split: train on January through April 2025, evaluate May 2025, and score June 2025.

![ML notebook train test score logic](assets/aidp_ml_lab/screenshots/01_ml_notebook_train_test_score_logic.png)

### Step 4 - Build the training frame

The notebook reads:

- `gold_claims_summary`
- `gold_capacity_event_latest`
- `gold_provider_accreditation_summary`
- `gold_spatial_access_insights`

It then joins the context at district or district-month level and creates a training frame at:

```text
service_month + district_id + program_code + claim_type
```

Expected result:

The frame contains both claims measures and context features needed to prioritize review.

### Step 5 - Train, test, and track the baseline model

The notebook uses a Spark ML logistic regression baseline when enough label classes exist. It fits the model on January through April 2025, evaluates it on May 2025, and only then scores June 2025.

The notebook also uses MLflow when available:

```python
import mlflow

experiment_name = "MPHA Claims Denial Risk Prediction"
mlflow.set_experiment(experiment_name)
mlflow.autolog()

with mlflow.start_run(run_name="claims_denial_risk_v1_baseline"):
    # Train model, evaluate the held-out month, log metrics, and publish scoring output.
```

Tracked parameters include:

- model version
- target
- feature grain
- training row count
- test row count
- scoring row count
- train label class count
- test label class count
- numeric feature count
- categorical feature count

Tracked metrics include:

- training AUC
- test AUC
- average denial risk score
- high-risk slice count
- medium-risk slice count
- scored row count

Expected result:

The experiment run is visible in AIDP Experiments, with the latest run showing `FINISHED`, `model_auc_training`, `model_auc_test`, and `scored_row_count = 102`.

![AIDP experiment list](assets/aidp_ml_lab/screenshots/02_experiments_list.png)

![AIDP finished train test run](assets/aidp_ml_lab/screenshots/02_experiment_runs_train_test_finished.png)

### Step 6 - Compare experiment runs

Return to **Experiments** and open `MPHA Claims Denial Risk Prediction`.

Use:

- the run list to inspect recent runs
- the compare view to compare runs by metrics
- run details to inspect parameters, metrics, and artifacts

Suggested comparison examples:

| Run | Difference | Review decision |
| --- | --- | --- |
| Baseline logistic regression | Claims and operational features | Good starting point for explainability. |
| Expanded feature set | Adds provider and spatial context | Use if test metrics improve without over-expanding review workload. |
| Threshold tuning | Adjusts high-risk cutoff | Use if business wants a smaller or larger review queue. |

Selection rule:

Choose the run that gives a defensible, explainable review-prioritization queue. Do not choose purely by metric if it creates an unrealistic operations workload.

Validated run checkpoint:

- Run name: `claims_denial_risk_v1_baseline`
- Status: `FINISHED`
- Logged model artifact: `claims_denial_risk_pipeline`
- Training rows: `410`
- Test rows: `110`
- Scoring rows: `102`
- Training months: `2025-01-01` to `2025-04-01`
- Test service month: `2025-05-01`
- Scored service month: `2025-06-01`

Open the run Overview and confirm the logged model artifact.

![AIDP run overview with logged model](assets/aidp_ml_lab/screenshots/03_ml_run_overview_finished.png)

Open Metrics and confirm training and held-out test metrics.

![AIDP run metrics](assets/aidp_ml_lab/screenshots/04_ml_run_metrics_train_test.png)

Open Parameters and confirm the train, test, and score split.

![AIDP run parameters](assets/aidp_ml_lab/screenshots/05_ml_run_parameters_train_test_score.png)

### Step 7 - Optionally register the selected model

In AIDP Workbench:

1. Open **Models**.
2. Click **Register**.
3. Enter:
   - Model name: `claim_denial_risk`
   - Version: `v1`
   - Description: `Predicts high-risk claims slices for operational review prioritization`
4. Choose model location: `Master catalog > e2eindustrydemos > default`.
5. Select the logged model artifact `claims_denial_risk_pipeline`.
6. Add optional metadata:
   - `business_owner=claims_operations`
   - `review_use_case=denial_prioritization`
   - `serving_pattern=batch_score`
7. Click **Register**.

Expected result:

The model is visible in AIDP Models with version, metrics, artifacts, and lineage back to the experiment run. Register only after the run's training metric, held-out test metric, and review-queue size are acceptable for the business use case.

![AIDP register model dialog](assets/aidp_ml_lab/screenshots/05_register_model_dialog.png)

![AIDP registered model list](assets/aidp_ml_lab/screenshots/06_models_catalog_list.png)

![AIDP registered model detail](assets/aidp_ml_lab/screenshots/07_registered_model_detail.png)

### Step 8 - Batch score the latest month

After the test metrics are logged, run the scoring cells in the notebook. The scoring slice is the latest service month.

The notebook produces:

- `denial_risk_score`
- `likely_denial_bucket`
- `review_priority`
- `model_version`
- `score_run_date`

If the training set does not contain enough class variation, the notebook falls back to a transparent weighted scoring path. This keeps the workshop runnable while still explaining the difference between a trained model and a fallback business score.

### Step 9 - Publish scored outputs

The notebook writes two outputs:

1. `gold_claims_denial_risk_scores`
2. `gold_claims_denial_model_run_summary`

The model run summary includes the training months, held-out test month, scored service month, row counts, label-class counts, train AUC, test AUC, and score distribution metrics.

Recommended scoring table columns:

- service month
- district id
- district name
- program code
- coverage program
- claim type
- claims submitted
- denied claims
- denial rate
- average processing days
- supply alert count
- triage total
- public-health pressure index
- accreditation risk band
- denial risk score
- likely denial bucket
- review priority
- model version
- score run date

### Step 10 - Use the score in OAC and the copilot

OAC extension ideas:

- KPI for high-risk slices
- table sorted by review priority
- scatter chart comparing actual denial rate and predicted risk
- filter by district, program, claim type, and risk bucket

Copilot extension ideas:

- Ask which denial-risk slices should be reviewed first.
- Ask why a district is high risk.
- Ask the policy copilot what playbook actions apply to the high-risk district.

## Completion criteria

The lab is complete when:

1. An AIDP Experiment exists.
2. At least one notebook run is logged to the experiment.
3. The run contains parameters and metrics.
4. The run includes a held-out test metric, not only a training metric.
5. The selected run is registered or ready to register as a model.
6. Batch scoring output is published.
7. The scored output can be explained in business terms.

## Expected business outcome

Participants can explain how the workshop moves from descriptive analytics to predictive claims operations:

```text
Claims star schema -> train/test/evaluate notebook -> AIDP Experiment -> registered model -> batch scores -> OAC and copilot action queue
```
