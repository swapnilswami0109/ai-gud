#!/usr/bin/env python3
"""Show the leaderboard CSV in the results folder in descending order of accuracy."""
import argparse
import pandas as pd
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--results", default="results")
args = parser.parse_args()

lb = Path(args.results) / "leaderboard.csv"
if not lb.exists():
    print("No leaderboard found")
    raise SystemExit(0)

df = pd.read_csv(lb)
df = df.sort_values(by=["accuracy", "f1"], ascending=False)
print(df.to_string(index=False))
