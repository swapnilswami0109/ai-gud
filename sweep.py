#!/usr/bin/env python3
"""Hyperparameter sweep using Optuna for RandomForest.

Usage:
  python scripts/sweep.py --data data/sample.csv --target target --trials 30 --results-out results

This will run an Optuna study, save best model and append metrics to leaderboard.
"""
import argparse
import json
import os
import time
from pathlib import Path

import joblib
import optuna
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def preprocess(df):
    encoders = {}
    # convert object or category dtypes to numeric via LabelEncoder
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    return df, encoders


def objective(trial, X, y):
    n_estimators = trial.suggest_int("n_estimators", 50, 400)
    max_depth = trial.suggest_int("max_depth", 3, 30)
    min_samples_split = trial.suggest_int("min_samples_split", 2, 20)

    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=42,
        n_jobs=1,
    )
    # simple CV via train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=42)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_val)
    acc = accuracy_score(y_val, preds)
    return acc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/sample.csv")
    parser.add_argument("--target", required=True)
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--results-out", default="results")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise SystemExit(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    if args.target not in df.columns:
        raise SystemExit(f"Target column '{args.target}' not in dataset")

    features = [c for c in df.columns if c != args.target]
    df_proc, encoders = preprocess(df[features + [args.target]].copy())
    X = df_proc[features].values
    y = df_proc[args.target].values

    study = optuna.create_study(direction="maximize")
    func = lambda trial: objective(trial, X, y)
    study.optimize(func, n_trials=args.trials)

    best_params = study.best_params

    # Train final model on full dataset with best params
    best_model = RandomForestClassifier(**best_params, random_state=42)
    best_model.fit(X, y)

    ts = int(time.time())
    Path(args.results_out).mkdir(parents=True, exist_ok=True)

    model_path = os.path.join(args.results_out, f"rf_best_{ts}.joblib")
    joblib.dump({"model": best_model, "features": features, "encoders": encoders}, model_path)

    # Log experiment to MLflow
    mlflow.set_experiment("ai_guardian_experiments")
    with mlflow.start_run(run_name=f"sweep_{ts}"):
        mlflow.log_params(best_params)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1", f1)
        mlflow.sklearn.log_model(best_model, artifact_path="model")

    # Evaluate on same data (for small demos). In real workflow, use held-out test set.
    preds = best_model.predict(X)
    acc = float(accuracy_score(y, preds))
    f1 = float(f1_score(y, preds, average="binary" if len(set(y))==2 else "macro"))

    metrics = {
        "timestamp": ts,
        "model_path": model_path,
        "data": str(data_path),
        "target": args.target,
        "accuracy": acc,
        "f1": f1,
        "best_params": best_params,
    }

    metrics_path = os.path.join(args.results_out, f"sweep_metrics_{ts}.json")
    with open(metrics_path, "w") as fh:
        json.dump(metrics, fh, indent=2)

    leaderboard_csv = os.path.join(args.results_out, "leaderboard.csv")
    row = pd.DataFrame([metrics])
    if os.path.exists(leaderboard_csv):
        row.to_csv(leaderboard_csv, mode="a", header=False, index=False)
    else:
        row.to_csv(leaderboard_csv, index=False)

    print("Sweep completed")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
