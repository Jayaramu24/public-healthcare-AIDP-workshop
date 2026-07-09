# Public Healthcare AIDP Workshop
# ML notebook: Gold-serving claims inputs -> train, test, evaluate, and score denial risk.
#
# Run `aidp_gold_pyspark.py` first so the Gold stage files exist.

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.functions import vector_to_array

# -----------------------------------------------------------------------------
# 1. Import MLflow when it is available.
# AIDP Experiments use MLflow tracking; the notebook still runs in notebook-only
# mode if the runtime does not expose MLflow packages.
# -----------------------------------------------------------------------------
try:
    import mlflow
    import mlflow.pyfunc as mlflow_pyfunc

    MLFLOW_AVAILABLE = True
except ImportError:
    mlflow = None
    mlflow_pyfunc = None
    MLFLOW_AVAILABLE = False


# -----------------------------------------------------------------------------
# 2. Configure Gold-stage input, experiment names, and scoring metadata.
# The Gold-stage path should match the mounted AIDP volume used in Labs 1-4.
# -----------------------------------------------------------------------------
gold_stage_base = "/Volumes/e2eindustrydemos/default/e2eindustrydemovol/gold_stage"
model_version = "claims_denial_risk_v1"
experiment_name = "MPHA Claims Denial Risk Prediction"
mlflow_run_name = f"{model_version}_baseline"
model_artifact_path = "claims_denial_risk_pipeline"
enable_mlflow_tracking = True
score_run_date = F.to_date(F.lit("2025-07-01"))


# -----------------------------------------------------------------------------
# 3. Shared CSV and ratio helpers.
# Gold-stage CSVs are read as strings, then typed in each business-specific
# select block below.
# -----------------------------------------------------------------------------
def read_stage_csv(name):
    return spark.read.option("header", "true").csv(f"{gold_stage_base}/{name}")


def write_stage_csv(frame, name):
    frame.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{gold_stage_base}/{name}")


def safe_ratio(numerator, denominator):
    return F.when(F.col(denominator) > 0, F.col(numerator) / F.col(denominator)).otherwise(F.lit(0.0))


# -----------------------------------------------------------------------------
# 4. Optional model artifact for registry demonstration.
# The Spark model does the workshop scoring. This lightweight pyfunc model is
# logged as an artifact so participants can register a model from the experiment.
# -----------------------------------------------------------------------------
if MLFLOW_AVAILABLE:
    class ClaimsDenialRiskPyfuncModel(mlflow_pyfunc.PythonModel):
        def predict(self, context, model_input):
            import numpy as np
            import pandas as pd

            data = model_input.copy()
            index = data.index

            def numeric_series(name, default=0.0):
                if name in data.columns:
                    return pd.to_numeric(data[name], errors="coerce").fillna(default)
                return pd.Series(default, index=index)

            denial_rate = numeric_series("denial_rate").clip(0, 1)
            processing_pressure = (numeric_series("avg_processing_days") / 45.0).clip(0, 1)
            payment_gap = (1.0 - numeric_series("payment_yield", 1.0)).clip(0, 1)
            occupancy_pressure = numeric_series("avg_current_occupancy_rate").clip(0, 1)
            wait_pressure = (numeric_series("latest_avg_ed_wait_minutes") / 240.0).clip(0, 1)
            supply_pressure = (numeric_series("supply_alert_count") / 10.0).clip(0, 1)

            score = (
                0.55 * denial_rate
                + 0.15 * processing_pressure
                + 0.10 * payment_gap
                + 0.10 * occupancy_pressure
                + 0.05 * wait_pressure
                + 0.05 * supply_pressure
            )
            return np.round(np.clip(score, 0, 1), 4)
else:
    ClaimsDenialRiskPyfuncModel = None


# -----------------------------------------------------------------------------
# 5. Load the Claims Gold summary and derive payment yield.
# This is the core ML grain: service month, district, coverage program, and claim
# type.
# -----------------------------------------------------------------------------
claims = (
    read_stage_csv("gold_claims_summary")
    .select(
        F.to_date("service_month").alias("service_month"),
        "district_id",
        "coverage_program",
        "program_code",
        "claim_type",
        F.col("claims_submitted").cast("int").alias("claims_submitted"),
        F.col("approved_claims").cast("int").alias("approved_claims"),
        F.col("denied_claims").cast("int").alias("denied_claims"),
        F.col("pending_claims").cast("int").alias("pending_claims"),
        F.col("total_submitted_amount").cast("double").alias("total_submitted_amount"),
        F.col("total_approved_amount").cast("double").alias("total_approved_amount"),
        F.col("total_paid_amount").cast("double").alias("total_paid_amount"),
        F.col("avg_processing_days").cast("double").alias("avg_processing_days"),
        F.col("denial_rate").cast("double").alias("denial_rate"),
    )
    .withColumn("payment_yield", F.round(safe_ratio("total_paid_amount", "total_submitted_amount"), 4))
)


# -----------------------------------------------------------------------------
# 6. Add provider, capacity, and spatial context.
# These context tables let the model learn from accreditation risk, facility
# pressure, supply alerts, public-health pressure, and access distance.
# -----------------------------------------------------------------------------
provider_raw = read_stage_csv("gold_provider_accreditation_summary")
accreditation_band_column = (
    "accreditation_risk_band"
    if "accreditation_risk_band" in provider_raw.columns
    else "accreditation_pressure_band"
)

facility_district_lookup = provider_raw.select("facility_id", "district_id").dropDuplicates(["facility_id"])

capacity = (
    read_stage_csv("gold_capacity_event_latest")
    .select(
        "facility_id",
        F.col("current_occupancy_rate").cast("double").alias("current_occupancy_rate"),
        F.col("avg_ed_wait_minutes").cast("double").alias("latest_avg_ed_wait_minutes"),
        F.col("triage_total").cast("double").alias("triage_total"),
        F.col("supply_alert_count").cast("double").alias("supply_alert_count"),
    )
    .join(facility_district_lookup, "facility_id", "left")
    .filter(F.col("district_id").isNotNull())
)

capacity_context = capacity.groupBy("district_id").agg(
    F.round(F.avg("current_occupancy_rate"), 4).alias("avg_current_occupancy_rate"),
    F.round(F.avg("latest_avg_ed_wait_minutes"), 1).alias("latest_avg_ed_wait_minutes"),
    F.round(F.sum("triage_total"), 1).alias("triage_total"),
    F.round(F.sum("supply_alert_count"), 1).alias("supply_alert_count"),
)


provider = provider_raw.select(
    "district_id",
    F.col("accreditation_score").cast("double").alias("accreditation_score"),
    F.col("corrective_action_count").cast("double").alias("corrective_action_count"),
    F.col("days_to_expiry").cast("double").alias("days_to_expiry"),
    F.col(accreditation_band_column).alias("accreditation_risk_band"),
)

provider_context = (
    provider.withColumn(
        "accreditation_risk_rank",
        F.when(F.col("accreditation_risk_band") == "High", 3)
        .when(F.col("accreditation_risk_band") == "Medium", 2)
        .otherwise(1),
    )
    .groupBy("district_id")
    .agg(
        F.round(F.avg("accreditation_score"), 2).alias("avg_accreditation_score"),
        F.round(F.sum("corrective_action_count"), 1).alias("total_corrective_action_count"),
        F.round(F.min("days_to_expiry"), 0).alias("min_days_to_expiry"),
        F.max("accreditation_risk_rank").alias("max_accreditation_risk_rank"),
    )
    .withColumn(
        "accreditation_risk_band",
        F.when(F.col("max_accreditation_risk_rank") >= 3, "High")
        .when(F.col("max_accreditation_risk_rank") == 2, "Medium")
        .otherwise("Watch"),
    )
    .drop("max_accreditation_risk_rank")
)


spatial_context = read_stage_csv("gold_spatial_access_insights").select(
    "district_id",
    "district_name",
    F.col("public_health_pressure_index").cast("double").alias("public_health_pressure_index"),
    F.col("residents_per_facility").cast("double").alias("residents_per_facility"),
    F.col("avg_travel_distance_km").cast("double").alias("avg_travel_distance_km"),
)


# -----------------------------------------------------------------------------
# 7. Build the ML feature frame and label.
# `high_denial_flag` is the supervised target; additional flags expose operations
# stress and slow processing as model features.
# -----------------------------------------------------------------------------
scoring_frame = (
    claims.join(capacity_context, "district_id", "left")
    .join(provider_context, "district_id", "left")
    .join(spatial_context, "district_id", "left")
    .na.fill(
        {
            "avg_current_occupancy_rate": 0.0,
            "latest_avg_ed_wait_minutes": 0.0,
            "triage_total": 0.0,
            "supply_alert_count": 0.0,
            "avg_accreditation_score": 85.0,
            "total_corrective_action_count": 0.0,
            "min_days_to_expiry": 365.0,
            "public_health_pressure_index": 0.0,
            "residents_per_facility": 0.0,
            "avg_travel_distance_km": 0.0,
            "accreditation_risk_band": "Watch",
        }
    )
    .withColumn("high_denial_flag", F.when(F.col("denial_rate") >= 0.10, F.lit(1.0)).otherwise(F.lit(0.0)))
    .withColumn("slow_processing_flag", F.when(F.col("avg_processing_days") >= 18.0, F.lit(1.0)).otherwise(F.lit(0.0)))
    .withColumn(
        "operations_stress_flag",
        F.when((F.col("triage_total") >= 120.0) | (F.col("supply_alert_count") >= 2.0), F.lit(1.0)).otherwise(F.lit(0.0)),
    )
)


# -----------------------------------------------------------------------------
# 8. Split the data by time.
# The validated workshop split trains on historical months, evaluates on the
# held-out May 2025 month, and scores the latest June 2025 month.
# -----------------------------------------------------------------------------
service_months = [
    row["service_month"]
    for row in scoring_frame.select("service_month").distinct().orderBy("service_month").collect()
]

if len(service_months) >= 3:
    latest_service_month = service_months[-1]
    test_service_month = service_months[-2]
    train_frame = scoring_frame.filter(F.col("service_month") < F.lit(test_service_month))
    test_frame = scoring_frame.filter(F.col("service_month") == F.lit(test_service_month))
    score_frame = scoring_frame.filter(F.col("service_month") == F.lit(latest_service_month))
else:
    latest_service_month = service_months[-1]
    test_service_month = latest_service_month
    train_frame, test_frame = scoring_frame.randomSplit([0.8, 0.2], seed=42)
    score_frame = scoring_frame.filter(F.col("service_month") == F.lit(latest_service_month))

training_row_count = train_frame.count()
test_row_count = test_frame.count()
scoring_row_count = score_frame.count()
train_label_class_count = train_frame.select("high_denial_flag").distinct().count()
test_label_class_count = test_frame.select("high_denial_flag").distinct().count()
can_train_model = training_row_count >= 20 and train_label_class_count >= 2
can_evaluate_model = test_row_count > 0 and test_label_class_count >= 2


# -----------------------------------------------------------------------------
# 9. Define feature columns and Spark ML pipeline.
# Categorical features are indexed and one-hot encoded; numeric and encoded
# columns are assembled into a single feature vector for logistic regression.
# -----------------------------------------------------------------------------
numeric_features = [
    "claims_submitted",
    "approved_claims",
    "pending_claims",
    "total_submitted_amount",
    "total_paid_amount",
    "payment_yield",
    "avg_processing_days",
    "supply_alert_count",
    "triage_total",
    "avg_current_occupancy_rate",
    "latest_avg_ed_wait_minutes",
    "public_health_pressure_index",
    "avg_accreditation_score",
    "total_corrective_action_count",
    "min_days_to_expiry",
    "residents_per_facility",
    "avg_travel_distance_km",
    "slow_processing_flag",
    "operations_stress_flag",
]

categorical_features = ["district_id", "program_code", "claim_type", "accreditation_risk_band"]
index_output_columns = [f"{name}_index" for name in categorical_features]
encoded_output_columns = [f"{name}_encoded" for name in categorical_features]

indexers = [StringIndexer(inputCol=name, outputCol=f"{name}_index", handleInvalid="keep") for name in categorical_features]
encoder = OneHotEncoder(inputCols=index_output_columns, outputCols=encoded_output_columns, handleInvalid="keep")
assembler = VectorAssembler(inputCols=numeric_features + encoded_output_columns, outputCol="features", handleInvalid="keep")
classifier = LogisticRegression(
    featuresCol="features",
    labelCol="high_denial_flag",
    predictionCol="prediction",
    probabilityCol="probability",
    rawPredictionCol="rawPrediction",
    maxIter=30,
    regParam=0.05,
)

training_pipeline = Pipeline(stages=indexers + [encoder, assembler, classifier])
mlflow_run_active = False
model_artifact_logged = False
model_auc_training = None
model_auc_test = None

# -----------------------------------------------------------------------------
# 10. Start AIDP Experiment tracking.
# Parameters record the exact split, grain, feature counts, and row counts so the
# run is auditable after the notebook completes.
# -----------------------------------------------------------------------------
if enable_mlflow_tracking and MLFLOW_AVAILABLE:
    try:
        mlflow.set_experiment(experiment_name)
        mlflow.autolog()
        mlflow.start_run(run_name=mlflow_run_name)
        mlflow_run_active = True
        mlflow.log_param("model_version", model_version)
        mlflow.log_param("target", "high_denial_flag")
        mlflow.log_param("grain", "service_month|district_id|program_code|claim_type")
        mlflow.log_param("train_months", f"{service_months[0]} to {service_months[-3]}" if len(service_months) >= 3 else "random_split_train")
        mlflow.log_param("test_service_month", str(test_service_month))
        mlflow.log_param("scored_service_month", str(latest_service_month))
        mlflow.log_param("training_row_count", training_row_count)
        mlflow.log_param("test_row_count", test_row_count)
        mlflow.log_param("scoring_row_count", scoring_row_count)
        mlflow.log_param("train_label_class_count", train_label_class_count)
        mlflow.log_param("test_label_class_count", test_label_class_count)
        mlflow.log_param("numeric_feature_count", len(numeric_features))
        mlflow.log_param("categorical_feature_count", len(categorical_features))
        mlflow.log_param("model_artifact_path", model_artifact_path)
    except Exception as exc:
        print(f"MLflow experiment tracking was skipped: {exc}")
        mlflow_run_active = False
elif enable_mlflow_tracking:
    print("MLflow package is not available in this runtime. Continuing with notebook-only scoring.")

# -----------------------------------------------------------------------------
# 11. Train, evaluate, and score.
# If the data slice is too small or has only one label class, the notebook falls
# back to an explainable weighted-score formula instead of failing the workshop.
# -----------------------------------------------------------------------------
if can_train_model:
    training_model = training_pipeline.fit(train_frame)
    try:
        evaluator = BinaryClassificationEvaluator(
            labelCol="high_denial_flag",
            rawPredictionCol="rawPrediction",
            metricName="areaUnderROC",
        )
        model_auc_training = float(evaluator.evaluate(training_model.transform(train_frame)))
        if can_evaluate_model:
            model_auc_test = float(evaluator.evaluate(training_model.transform(test_frame)))
    except Exception as exc:
        print(f"Model AUC calculation was skipped: {exc}")
    if mlflow_run_active:
        try:
            input_example = train_frame.select(numeric_features).limit(5).toPandas()
            mlflow_pyfunc.log_model(
                artifact_path=model_artifact_path,
                python_model=ClaimsDenialRiskPyfuncModel(),
                input_example=input_example,
            )
            model_artifact_logged = True
            mlflow.log_param("model_artifact_logged", "true")
        except Exception as exc:
            print(f"MLflow model artifact logging was skipped: {exc}")
    scored_frame = training_model.transform(score_frame).withColumn(
        "denial_risk_score",
        F.round(vector_to_array("probability")[1], 2),
    )
else:
    scored_frame = score_frame.withColumn(
        "denial_risk_score",
        F.round(
            F.least(
                F.lit(0.95),
                F.col("denial_rate") * F.lit(2.2)
                + F.least(F.col("avg_processing_days") / F.lit(30.0), F.lit(1.0)) * F.lit(0.15)
                + F.least(F.col("public_health_pressure_index") / F.lit(100.0), F.lit(1.0)) * F.lit(0.15)
                + F.least(F.col("supply_alert_count") / F.lit(3.0), F.lit(1.0)) * F.lit(0.10)
                + F.when(F.col("accreditation_risk_band") == "High", F.lit(0.15))
                .when(F.col("accreditation_risk_band") == "Medium", F.lit(0.08))
                .otherwise(F.lit(0.03)),
            ),
            2,
        ),
    )

# -----------------------------------------------------------------------------
# 12. Convert model scores into an operational review queue.
# The bucket and row-number priority turn model output into something Claims
# operations can triage in OAC or AI Lakehouse.
# -----------------------------------------------------------------------------
priority_window = Window.partitionBy("service_month").orderBy(
    F.col("denial_risk_score").desc(),
    F.col("denial_rate").desc(),
    F.col("avg_processing_days").desc(),
)

gold_claims_denial_risk_scores = (
    scored_frame.withColumn(
        "likely_denial_bucket",
        F.when(F.col("denial_risk_score") >= 0.70, "High")
        .when(F.col("denial_risk_score") >= 0.55, "Medium")
        .otherwise("Watch"),
    )
    .withColumn("review_priority", F.row_number().over(priority_window))
    .withColumn("model_version", F.lit(model_version))
    .withColumn("score_run_date", score_run_date)
    .select(
        "service_month",
        "district_id",
        "district_name",
        "program_code",
        "coverage_program",
        "claim_type",
        "claims_submitted",
        "denied_claims",
        "denial_rate",
        "avg_processing_days",
        "supply_alert_count",
        "triage_total",
        "public_health_pressure_index",
        "accreditation_risk_band",
        "denial_risk_score",
        "likely_denial_bucket",
        "review_priority",
        "model_version",
        "score_run_date",
    )
)

# -----------------------------------------------------------------------------
# 13. Log final run metrics.
# These are the values participants should verify in the AIDP Experiments run:
# training AUC, held-out test AUC, scored rows, and review-queue size.
# -----------------------------------------------------------------------------
score_metrics = gold_claims_denial_risk_scores.agg(
    F.count("*").alias("scored_row_count"),
    F.round(F.avg("denial_risk_score"), 4).alias("avg_denial_risk_score"),
    F.sum(F.when(F.col("likely_denial_bucket") == "High", F.lit(1)).otherwise(F.lit(0))).alias("high_risk_slice_count"),
    F.sum(F.when(F.col("likely_denial_bucket") == "Medium", F.lit(1)).otherwise(F.lit(0))).alias("medium_risk_slice_count"),
).first()

if mlflow_run_active:
    try:
        mlflow.log_metric("model_auc_training", float(model_auc_training) if model_auc_training is not None else -1.0)
        mlflow.log_metric("model_auc_test", float(model_auc_test) if model_auc_test is not None else -1.0)
        mlflow.log_metric("avg_denial_risk_score", float(score_metrics["avg_denial_risk_score"]))
        mlflow.log_metric("high_risk_slice_count", int(score_metrics["high_risk_slice_count"]))
        mlflow.log_metric("medium_risk_slice_count", int(score_metrics["medium_risk_slice_count"]))
        mlflow.log_metric("scored_row_count", int(score_metrics["scored_row_count"]))
        mlflow.end_run()
    except Exception as exc:
        print(f"MLflow metric logging was skipped: {exc}")

# -----------------------------------------------------------------------------
# 14. Build a compact run-summary table.
# This summary is written beside the score output so the batch score can be tied
# back to the model version and experiment run context.
# -----------------------------------------------------------------------------
model_run_summary = spark.createDataFrame(
    [
        (
            model_version,
            experiment_name,
            f"{service_months[0]} to {service_months[-3]}" if len(service_months) >= 3 else "random_split_train",
            str(test_service_month),
            str(latest_service_month),
            int(training_row_count),
            int(test_row_count),
            int(scoring_row_count),
            int(train_label_class_count),
            int(test_label_class_count),
            float(model_auc_training) if model_auc_training is not None else -1.0,
            float(model_auc_test) if model_auc_test is not None else -1.0,
            float(score_metrics["avg_denial_risk_score"]),
            int(score_metrics["high_risk_slice_count"]),
            int(score_metrics["medium_risk_slice_count"]),
            "mlflow_experiment" if mlflow_run_active else "notebook_only",
        )
    ],
    [
        "model_version",
        "experiment_name",
        "training_months",
        "test_service_month",
        "scored_service_month",
        "training_row_count",
        "test_row_count",
        "scoring_row_count",
        "train_label_class_count",
        "test_label_class_count",
        "model_auc_training",
        "model_auc_test",
        "avg_denial_risk_score",
        "high_risk_slice_count",
        "medium_risk_slice_count",
        "tracking_mode",
    ],
)

# -----------------------------------------------------------------------------
# 15. Publish outputs and print the handoff.
# Downstream users can add `gold_claims_denial_risk_scores` to AI Lakehouse or
# OAC and use `gold_claims_denial_model_run_summary` for lineage.
# -----------------------------------------------------------------------------
write_stage_csv(gold_claims_denial_risk_scores, "gold_claims_denial_risk_scores")
write_stage_csv(model_run_summary, "gold_claims_denial_model_run_summary")

print(
    f"Trained claims denial model on months before {test_service_month}, "
    f"evaluated on {test_service_month}, and scored {latest_service_month}."
)
if not can_train_model:
    print("Used the fallback weighted-score path because the training slice did not contain enough rows or both label classes.")
elif not can_evaluate_model:
    print("Model was trained, but test AUC was skipped because the test slice did not contain both label classes.")
print(f"Published gold_claims_denial_risk_scores under {gold_stage_base}/gold_claims_denial_risk_scores")
print(f"Published gold_claims_denial_model_run_summary under {gold_stage_base}/gold_claims_denial_model_run_summary")
