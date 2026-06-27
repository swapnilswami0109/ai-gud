#!/usr/bin/env python3
"""Evaluate a saved model on a dataset and print metrics.

Usage:
  python scripts/evaluate.py --model models/rf_model_*.joblib --data data/sample.csv --target target
"""
import argparse
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    model_obj = joblib.load(args.model)
    model = model_obj.get("model") if isinstance(model_obj, dict) else model_obj
    features = model_obj.get("features") if isinstance(model_obj, dict) else None

    df = pd.read_csv(args.data)
    if args.target not in df.columns:
        raise SystemExit("Target column missing from dataset")

    if features is None:
        features = [c for c in df.columns if c != args.target]

    X = df[features].copy()
    y = df[args.target].values

    preds = model.predict(X)
    acc = accuracy_score(y, preds)
    f1 = f1_score(y, preds, average="binary" if len(set(y))==2 else "macro")

    out = {"accuracy": float(acc), "f1": float(f1)}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
