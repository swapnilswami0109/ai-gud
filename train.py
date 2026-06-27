#!/usr/bin/env python3
"""Simple reproducible trainer for the AI Guardian OS hackathon submission.

Usage:
  python scripts/train.py --data data/sample.csv --target target --model-out models/ --results-out results/

This script trains a RandomForest on a CSV file and saves the model and metrics.
"""
import argparse
import json
import os
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import mlflow
import mlflow.sklearn


def simple_preprocess(df):
    encoders = {}
    for col in df.columns:
        if df[col].dtype == object:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
    return df, encoders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/sample.csv")
    parser.add_argument("--target", required=True)
    parser.add_argument("--model-out", default="models")
    parser.add_argument("--results-out", default="results")
    parser.add_argument("--val-size", type=float, default=0.1, help="Validation split fraction (of the full dataset)")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split fraction (of the full dataset)")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise SystemExit(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    if args.target not in df.columns:
        raise SystemExit(f"Target column '{args.target}' not in dataset")

    features = [c for c in df.columns if c != args.target]

    df_proc, encoders = simple_preprocess(df[features + [args.target]].copy())

    X = df_proc[features].values
    y = df_proc[args.target].values

    if args.val_size + args.test_size >= 1.0:
        raise SystemExit("val-size + test-size must be < 1.0")

    # First split off the test set
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )

    # Then split train and validation from the remaining portion
    val_relative = args.val_size / (1.0 - args.test_size) if args.val_size > 0 else 0.0
    if val_relative > 0:
        X_train, X_val, y_train, y_val = train_test_split(
            X_trainval, y_trainval, test_size=val_relative, random_state=args.random_state
        )
    else:
        X_train, y_train = X_trainval, y_trainval
        X_val, y_val = None, None

    model = RandomForestClassifier(n_estimators=200, random_state=args.random_state)
    model.fit(X_train, y_train)

    # Evaluate on validation if present else test
    eval_X, eval_y = (X_val, y_val) if X_val is not None else (X_test, y_test)
    preds = model.predict(eval_X)
    acc = float(accuracy_score(eval_y, preds))
    f1 = float(f1_score(eval_y, preds, average="binary" if len(np.unique(y))==2 else "macro"))

    ts = int(time.time())
    Path(args.model_out).mkdir(parents=True, exist_ok=True)
    Path(args.results_out).mkdir(parents=True, exist_ok=True)

    model_path = os.path.join(args.model_out, f"rf_model_{ts}.joblib")

    # Final evaluation on test set for reporting
    final_preds = model.predict(X_test)
    final_acc = float(accuracy_score(y_test, final_preds))
    final_f1 = float(f1_score(y_test, final_preds, average="binary" if len(np.unique(y))==2 else "macro"))

    metrics = {
        "timestamp": ts,
        "model_path": model_path,
        "data": str(data_path),
        "target": args.target,
        "validation_accuracy": acc,
        "validation_f1": f1,
        "test_accuracy": final_acc,
        "test_f1": final_f1,
    }

    # Log experiment to MLflow and save model
    mlflow.set_experiment("ai_guardian_experiments")
    with mlflow.start_run(run_name=f"train_{ts}"):
        mlflow.log_params({
            "n_estimators": 200,
            "random_state": args.random_state,
        })
        mlflow.log_metric("val_accuracy", acc)
        mlflow.log_metric("test_accuracy", final_acc)
        mlflow.log_metric("test_f1", final_f1)
        mlflow.sklearn.log_model(model, artifact_path="model")
        # save model locally as well
        joblib.dump({"model": model, "encoders": encoders, "features": features}, model_path)

    # write metrics json
    metrics_path = os.path.join(args.results_out, f"metrics_{ts}.json")
    with open(metrics_path, "w") as fh:
        json.dump(metrics, fh, indent=2)

    # append to leaderboard csv
    leaderboard_csv = os.path.join(args.results_out, "leaderboard.csv")
    row = pd.DataFrame([metrics])
    if os.path.exists(leaderboard_csv):
        row.to_csv(leaderboard_csv, mode="a", header=False, index=False)
    else:
        row.to_csv(leaderboard_csv, index=False)

    print("Training finished")
    print(json.dumps(metrics, indent=2))
if __name__ == "__main__":
    main()
