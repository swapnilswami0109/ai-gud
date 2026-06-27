#!/usr/bin/env python3
"""CI smoke test: start a run, log a simple sklearn model, register and promote it via MLflow client."""
import time
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import sklearn.ensemble
import numpy as np

TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "ci_smoke_experiment"
MODEL_NAME = "ci_smoke_model"

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

# small toy model
X = np.random.randn(50, 4)
y = (X.sum(axis=1) > 0).astype(int)
clf = sklearn.ensemble.RandomForestClassifier(n_estimators=10, random_state=42)
clf.fit(X, y)

with mlflow.start_run() as run:
    mlflow.log_param("smoke", True)
    mlflow.sklearn.log_model(clf, artifact_path="model")
    run_id = run.info.run_id

client = MlflowClient(tracking_uri=TRACKING_URI)
# ensure experiment exists
exp = client.get_experiment_by_name(EXPERIMENT_NAME)
print("Experiment:", exp.experiment_id if exp else None)

# create registered model if missing
try:
    client.create_registered_model(MODEL_NAME)
except Exception:
    pass

# create model version from run artifact
mv = client.create_model_version(name=MODEL_NAME, source=f"runs:/{run_id}/model", run_id=run_id)
print("Created model version:", mv.version)

# transition to Staging
client.transition_model_version_stage(name=MODEL_NAME, version=mv.version, stage="Staging")
print("Promoted to Staging")

print("CI MLflow smoke test completed OK")
