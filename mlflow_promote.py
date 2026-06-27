#!/usr/bin/env python3
"""Register and promote an MLflow model version given a run id.

Usage:
  python scripts/mlflow_promote.py --run-id <RUN_ID> --model-name <MODEL_NAME> --stage Staging
"""
import argparse
from mlflow.tracking import MlflowClient

parser = argparse.ArgumentParser()
parser.add_argument("--run-id", required=True)
parser.add_argument("--model-name", required=True)
parser.add_argument("--stage", default="Staging")
parser.add_argument("--tracking-uri", default="http://127.0.0.1:5000")
args = parser.parse_args()

client = MlflowClient(tracking_uri=args.tracking_uri)
try:
    client.create_registered_model(args.model_name)
except Exception:
    pass

mv = client.create_model_version(name=args.model_name, source=f"runs:/{args.run_id}/model", run_id=args.run_id)
print(f"Created model version {mv.version} for {args.model_name}")
client.transition_model_version_stage(name=args.model_name, version=mv.version, stage=args.stage)
print(f"Transitioned model {args.model_name} v{mv.version} to {args.stage}")
