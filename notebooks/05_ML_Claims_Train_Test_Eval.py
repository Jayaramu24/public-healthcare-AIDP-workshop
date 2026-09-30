# %% [markdown]
# # Before you run: your assigned environment
#
# Use your preloaded notebook when available. If restoring this common download,
# copy the exact administrator-assigned values into its setup cell:
# `participant_id`, `volume_base` (shared raw input) and `output_base` (your own
# output volume). In the Lakehouse notebooks and notebook 99 also set
# `target_catalog` and `target_schema`. Do not infer paths from your name or copy
# another participant's values from a screenshot. The administrator must enforce
# access permissions; string validation is not a security boundary.
#
# Notebook filenames do not change when lab numbers change. Run 01, 02, 03 and 04
# in order. Then follow the guide for 02B/03B, 05, the workflow and agents.
# Notebook 99 contains on-demand read-only inspection examples.
#
# Bronze/Silver/Gold overwrite only the assigned output snapshot. Lakehouse loads
# append missing keys and are safe to repeat with unchanged source/reference data;
# they do not update existing measures or implement general CDC. Do not change
# dimension members or source snapshots without a reviewed loading strategy.
#
# This common download changes configuration only, not the tested transformation
# logic. A restore into a different tenancy still requires its readiness and
# execution checks. Use Python as notebook default; select SQL only for SQL cells.
#
# For this ML notebook only participant_id and output_base are needed; it reads your staged Gold CSV, not raw files or AI Lakehouse.

# %% [markdown]
# # Claims denial risk: train, evaluate, score, and track
# This synthetic-data exercise predicts a segment's high-denial month using
# only its previous calendar month's outcomes and its known segment identity.
# It is not a model for deciding individual claims or benefits eligibility.
#
# Inputs: your Gold-stage claims summary. Outputs: June review scores, May
# evaluation results, an AIDP experiment, and the exact fitted model artifact.
# Set participant_id and output_base from your configuration sheet. Running again creates a new experiment run and
# replaces only your own score outputs. Missing MLflow or invalid splits fail
# explicitly; this test does not silently substitute a rules-based score.

# %%
from pathlib import Path
import json
import tempfile
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score, recall_score,
    f1_score, accuracy_score, confusion_matrix, brier_score_loss,
)
from pyspark.sql import functions as F

participant_id = "REPLACE_WITH_YOUR_PARTICIPANT_ID"
assert participant_id != "REPLACE_WITH_YOUR_PARTICIPANT_ID", "Set your assigned participant_id."
output_base = "REPLACE_WITH_YOUR_OUTPUT_VOLUME"
assert output_base.startswith("/Volumes/") and "REPLACE_" not in output_base, "Set your personal output volume."
output_base = output_base.rstrip("/")
gold_stage_base = f"{output_base}/gold_stage"
experiment_name = f"MPHA_{participant_id}_Claims_Denial_Risk"
threshold = 0.5
label_threshold = 0.10
random_seed = 42
print("OUTPUT:", output_base, "EXPERIMENT:", experiment_name)


# %% [markdown]
# ## Read trusted Gold and build features available before the prediction month
# The input is monthly by district, program, and claim type. A self-join aligns
# exactly the previous calendar month. It does not use current-month approval,
# payment, denial, or processing outcomes as features. January is excluded
# because the workshop has no December history. Missing history stays missing.
# Expected: unique segment-month keys and six source months; actual counts print.

# %%
keys = ["district_id", "program_code", "claim_type"]
history_columns = ["claims_submitted", "denial_rate", "pending_claims",
                   "avg_processing_days", "total_submitted_amount", "total_paid_amount"]
source = spark.read.option("header", "true").csv(f"{gold_stage_base}/gold_claims_summary")
claims = source.select(
    F.to_date("service_month").alias("service_month"), *keys,
    *[F.col(c).cast("double").alias(c) for c in history_columns],
).toPandas()
claims["service_month"] = pd.to_datetime(claims["service_month"])
assert not claims.duplicated(keys + ["service_month"]).any(), "Duplicate Gold segment-month keys."
assert claims[keys + ["service_month", "denial_rate"]].notna().all().all(), "Null keys or labels."
months = sorted(claims.service_month.unique())
assert len(months) >= 6, "Need six separate months for temporal validation."
previous = claims[keys + ["service_month"] + history_columns].copy()
previous["service_month"] += pd.DateOffset(months=1)
previous = previous.rename(columns={c: "prior_" + c for c in history_columns})
data = claims.merge(previous, on=keys + ["service_month"], how="left", validate="one_to_one")
data = data[data.service_month > months[0]].copy()
data["high_denial_flag"] = (data.denial_rate >= label_threshold).astype(int)
numeric_features = ["prior_" + c for c in history_columns]
features = keys + numeric_features
assert "denial_rate" not in features and all(c.startswith("prior_") for c in numeric_features)
train = data[data.service_month < months[-2]].copy()
test = data[data.service_month == months[-2]].copy()
score = data[data.service_month == months[-1]].copy()
assert len(train) >= 20 and len(test) > 0 and len(score) > 0, "Insufficient split rows."
assert train.high_denial_flag.nunique() == 2 and test.high_denial_flag.nunique() == 2, "Both label classes required."
assert train.service_month.max() < test.service_month.min() < score.service_month.min()
print("Source months:", [str(pd.Timestamp(m).date()) for m in months])
print("Rows:", {"source": len(claims), "train": len(train), "test": len(test), "score": len(score)})
print("Training label distribution:", train.high_denial_flag.value_counts().to_dict())
print("Test label distribution:", test.high_denial_flag.value_counts().to_dict())


# %% [markdown]
# ## Fit preprocessing and model on training rows only
# Imputation, category encoding, scaling, and logistic regression are fitted
# together. The May test set is not used for fitting or threshold tuning.
# Parameters: fixed random seed, threshold 0.5, regularization C=1.0.
# Expected: a FINISHED experiment with real test metrics and a saved pipeline.

# %%
preprocessor = ColumnTransformer([
    ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                           ("scale", StandardScaler())]), numeric_features),
    ("category", OneHotEncoder(handle_unknown="ignore"), keys),
])
model = Pipeline([("prepare", preprocessor),
                  ("classifier", LogisticRegression(C=1.0, max_iter=500, random_state=random_seed))])
mlflow.set_experiment(experiment_name)
with mlflow.start_run(run_name="prior_month_logistic_baseline") as run:
    run_id = run.info.run_id
    mlflow.log_params({
        "participant": participant_id, "grain": "month|district|program|claim_type",
        "train_start": str(train.service_month.min().date()),
        "train_end": str(train.service_month.max().date()),
        "test_month": str(test.service_month.min().date()),
        "score_month": str(score.service_month.min().date()),
        "label_threshold": label_threshold, "prediction_threshold": threshold,
        "feature_time": "previous_calendar_month_only", "random_seed": random_seed,
    })
    model.fit(train[features], train.high_denial_flag)
    test_probability = model.predict_proba(test[features])[:, 1]
    test_prediction = (test_probability >= threshold).astype(int)
    metrics = {
        "train_rows": len(train), "test_rows": len(test), "scored_rows": len(score),
        "test_roc_auc": roc_auc_score(test.high_denial_flag, test_probability),
        "test_average_precision": average_precision_score(test.high_denial_flag, test_probability),
        "test_accuracy": accuracy_score(test.high_denial_flag, test_prediction),
        "test_precision": precision_score(test.high_denial_flag, test_prediction, zero_division=0),
        "test_recall": recall_score(test.high_denial_flag, test_prediction, zero_division=0),
        "test_f1": f1_score(test.high_denial_flag, test_prediction, zero_division=0),
        "test_brier": brier_score_loss(test.high_denial_flag, test_probability),
        "test_positive_rate": float(test.high_denial_flag.mean()),
    }
    baseline_probability = np.full(len(test), train.high_denial_flag.mean())
    metrics["baseline_test_brier"] = brier_score_loss(test.high_denial_flag, baseline_probability)
    mlflow.log_metrics({k: float(v) for k, v in metrics.items()})
    # Save the actual fitted pipeline, not a substitute scoring formula.
    signature = infer_signature(train[features], model.predict(train[features]))
    # Trust only the NumPy dtype used by this locally trained pipeline; retain skops serialization.
    mlflow.sklearn.log_model(model, artifact_path="claims_denial_pipeline",
                            input_example=train[features].head(3), signature=signature,
                            skops_trusted_types=["numpy.dtype"])
    with tempfile.TemporaryDirectory() as evidence_dir:
        evidence = Path(evidence_dir) / "evaluation.json"
        evidence.write_text(json.dumps({"metrics": metrics, "features": features,
            "confusion_matrix": confusion_matrix(test.high_denial_flag, test_prediction).tolist(),
            "limitations": "Small synthetic aggregate dataset; not production insurance decisioning."}, indent=2))
        mlflow.log_artifact(str(evidence))
    score["denial_risk_score"] = model.predict_proba(score[features])[:, 1]
    score["likely_denial_bucket"] = np.where(score.denial_risk_score >= 0.7, "High",
                                  np.where(score.denial_risk_score >= 0.55, "Medium", "Watch"))
    score["mlflow_run_id"] = run_id
    output = score[["service_month"] + keys + ["denial_risk_score", "likely_denial_bucket", "mlflow_run_id"]].copy()
    output["service_month"] = output.service_month.dt.strftime("%Y-%m-%d")
    spark.createDataFrame(output).coalesce(1).write.mode("overwrite").option("header", "true").csv(
        f"{gold_stage_base}/gold_claims_denial_risk_scores")
    test_evidence = test[["service_month"] + keys + ["high_denial_flag"]].copy()
    test_evidence["service_month"] = test_evidence.service_month.dt.strftime("%Y-%m-%d")
    test_evidence["predicted_probability"] = test_probability
    test_evidence["predicted_label"] = test_prediction
    spark.createDataFrame(test_evidence).coalesce(1).write.mode("overwrite").option("header", "true").csv(
        f"{output_base}/ml/test_evaluation")
    print("METRICS:", json.dumps(metrics, sort_keys=True))
    print("CONFUSION_MATRIX:", confusion_matrix(test.high_denial_flag, test_prediction).tolist())


# %% [markdown]
# ## Reload the experiment artifact and validate persisted scores
# A model artifact is useful only if it can reproduce predictions. Reload it
# from MLflow and compare probabilities. Inspect the run in AIDP Experiments.
# Common errors: tracking authentication/runtime initialization, missing Gold
# files, or single-class test labels. Fix these errors; do not claim success.

# %%
reloaded = mlflow.sklearn.load_model(f"runs:/{run_id}/claims_denial_pipeline")
assert np.allclose(reloaded.predict_proba(score[features])[:, 1], score.denial_risk_score, atol=1e-10)
persisted = spark.read.option("header", "true").csv(f"{gold_stage_base}/gold_claims_denial_risk_scores")
assert persisted.count() == len(score), "Persisted score count mismatch."
assert mlflow.get_run(run_id).info.status == "FINISHED", "Experiment is not FINISHED."
persisted.orderBy(F.col("denial_risk_score").cast("double").desc()).show(10, truncate=False)
print("ML_E2E_SUCCESS", "run_id=", run_id, "score_rows=", persisted.count())


# %% [markdown]
# ## What you learned
# You used temporally valid features, fitted only on historical rows, evaluated
# a held-out month against a baseline, scored a later month, and verified the
# trained model's MLOps artifact. Results demonstrate the workflow; limited
# synthetic data does not establish production performance or fairness.
