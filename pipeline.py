"""
ai_gud.pipeline - Minimal, runnable AI trust pipeline helper functions.
Each function returns a small report (dict) that downstream steps can consume.
This implementation is lightweight and uses pandas only so it can run in the browser/CI
without heavy ML dependencies. Replace or extend each step with your real checks.
"""
from typing import Any, Dict, Optional
import pandas as pd
import re

def upload_dataset(file) -> pd.DataFrame:
    """Accepts a file-like object (from Streamlit uploader) or a path."""
    if hasattr(file, "read"):
        df = pd.read_csv(file)
    else:
        df = pd.read_csv(str(file))
    return df

def data_quality_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    rows = len(df)
    cols = df.columns.tolist()
    missing = df.isnull().mean().to_dict()  # fraction missing per column
    duplicated = int(df.duplicated().sum())
    issues = []
    if rows == 0:
        issues.append("empty_dataset")
    if duplicated > 0:
        issues.append("duplicates")
    high_missing = [c for c, v in missing.items() if v > 0.5]
    if high_missing:
        issues.append("high_missing:" + ",".join(high_missing))
    return {
        "rows": rows,
        "columns": cols,
        "missing_fraction": missing,
        "duplicated_rows": duplicated,
        "issues": issues,
    }

def fairness_audit(df: pd.DataFrame, sensitive_column: str, target_column: str) -> Dict[str, Any]:
    report: Dict[str, Any] = {}
    if sensitive_column not in df.columns or target_column not in df.columns:
        report["error"] = "columns_missing"
        return report
    grp = df.groupby(sensitive_column)[target_column]
    counts = grp.count().to_dict()
    positive_rate = (grp.mean()).to_dict()
    # compute disparity ratio (max/min) for positive rate among groups
    vals = [v for v in positive_rate.values() if pd.notnull(v)]
    disparity = None
    if vals:
        try:
            disparity = max(vals) / min(vals) if min(vals) != 0 else None
        except Exception:
            disparity = None
    report["counts"] = counts
    report["positive_rate"] = positive_rate
    report["disparity_ratio"] = disparity
    # simple flag
    report["fairness_pass"] = (disparity is None) or (disparity is not None and disparity <= 1.25)
    return report

PII_KEYWORDS = ["email", "phone", "ssn", "name", "address", "dob"]
PII_VALUE_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # simple SSN
    re.compile(r"\b\d{10}\b"),  # simple phone
    re.compile(r"@"),
]

def privacy_scan(df: pd.DataFrame) -> Dict[str, Any]:
    pii_columns = []
    pii_values = []
    for c in df.columns:
        low = c.lower()
        if any(k in low for k in PII_KEYWORDS):
            pii_columns.append(c)
        else:
            # inspect a few non-null values for patterns
            sample = df[c].dropna().astype(str).head(50).tolist()
            for v in sample:
                for pat in PII_VALUE_PATTERNS:
                    if pat.search(v):
                        pii_values.append({"column": c, "value": v})
                        break
    return {"pii_columns": pii_columns, "pii_value_examples": pii_values, "privacy_pass": len(pii_columns) == 0}


def explainability(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    # simple feature-target correlations for numeric columns
    res: Dict[str, Any] = {}
    if target_column not in df.columns:
        return {"error": "target_missing"}
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    if target_column not in numeric:
        # try coerce
        try:
            df[target_column] = pd.to_numeric(df[target_column])
            numeric = df.select_dtypes(include=["number"]).columns.tolist()
        except Exception:
            return {"error": "target_not_numeric"}
    corrs = df[numeric].corr()[target_column].drop(target_column, errors="ignore").to_dict()
    # rank features by absolute correlation
    ranked = sorted(corrs.items(), key=lambda x: abs(x[1]) if pd.notnull(x[1]) else 0, reverse=True)
    res["feature_correlations"] = corrs
    res["ranked_features"] = ranked
    res["explainability_pass"] = len(ranked) > 0
    return res


def risk_assessment(dq_report: Dict[str, Any], fairness_report: Dict[str, Any], privacy_report: Dict[str, Any]) -> Dict[str, Any]:
    score = 1.0
    reasons = []
    if dq_report.get("issues"):
        score -= 0.2
        reasons.append("data_quality_issues")
    if not fairness_report.get("fairness_pass", True):
        score -= 0.3
        reasons.append("fairness_concerns")
    if not privacy_report.get("privacy_pass", True):
        score -= 0.3
        reasons.append("privacy_concerns")
    score = max(0.0, score)
    risk_level = "low" if score >= 0.7 else "medium" if score >= 0.4 else "high"
    return {"risk_score": score, "risk_level": risk_level, "reasons": reasons}


def compliance_check(risk_report: Dict[str, Any]) -> Dict[str, Any]:
    # simple mapping: high risk -> fail
    pass_check = risk_report.get("risk_level") == "low"
    return {"compliance_pass": pass_check}


def ai_trust_score(reports: Dict[str, Any]) -> float:
    # combine simple signals into 0-1 score
    score = 0.0
    # data quality: if rows>0 and no major issues
    dq = reports.get("data_quality", {})
    if dq.get("rows", 0) > 0 and not any(i.startswith("high_missing") for i in dq.get("issues", [])):
        score += 0.3
    # fairness
    if reports.get("fairness", {}).get("fairness_pass", False):
        score += 0.2
    # privacy
    if reports.get("privacy", {}).get("privacy_pass", False):
        score += 0.2
    # explainability
    if reports.get("explainability", {}).get("explainability_pass", False):
        score += 0.2
    # risk (inverse)
    risk = reports.get("risk", {}).get("risk_score", 0)
    score += 0.1 * risk
    return round(min(1.0, score), 3)


def deployment_decision(score: float, threshold: float = 0.7) -> Dict[str, Any]:
    decision = "approve" if score >= threshold else "reject"
    return {"decision": decision, "threshold": threshold}


def run_pipeline(file, sensitive_column: Optional[str] = None, target_column: Optional[str] = None) -> Dict[str, Any]:
    df = upload_dataset(file)
    dq = data_quality_analysis(df)
    fa = fairness_audit(df, sensitive_column, target_column) if sensitive_column and target_column else {"skipped": True}
    ps = privacy_scan(df)
    ex = explainability(df, target_column) if target_column else {"skipped": True}
    ra = risk_assessment(dq, fa if not fa.get("skipped") else {}, ps)
    cc = compliance_check(ra)
    reports = {
        "data_quality": dq,
        "fairness": fa,
        "privacy": ps,
        "explainability": ex,
        "risk": ra,
        "compliance": cc,
    }
    score = ai_trust_score(reports)
    decision = deployment_decision(score)
    reports["ai_trust_score"] = score
    reports["deployment_decision"] = decision
    return reports
