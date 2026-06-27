import streamlit as st
import subprocess
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from pathlib import Path
import io
from database.database import get_connection
from database.logger import log
import time

st.set_page_config(page_title="Train / Sweep", page_icon="⚙️", layout="wide")
st.title("⚙️ Training & Sweep")

st.write("Run training or hyperparameter sweeps from the web UI.")

# select dataset from uploads or sample
UPLOAD_DIR = Path("uploads")
files = sorted(UPLOAD_DIR.glob("*"))
files = [f for f in files if f.is_file()]
files.insert(0, Path("data/sample.csv"))

selected = st.selectbox("Select dataset", files, format_func=lambda x: x.name)

# pick target column if possible
try:
    df = pd.read_csv(selected)
    columns = list(df.columns)
except Exception:
    columns = []

target = st.selectbox("Target column", columns)

col1, col2 = st.columns(2)
with col1:
    test_size = st.slider("Test size", 0.05, 0.4, 0.2)
    val_size = st.slider("Validation size", 0.0, 0.3, 0.1)
with col2:
    trials = st.number_input("Sweep trials", min_value=1, max_value=200, value=10)

run_train = st.button("Run Training")
run_sweep = st.button("Run Sweep")

output = st.empty()

results_path = Path("results")
results_path.mkdir(exist_ok=True)

# MLflow controls
st.divider()
st.header("MLflow")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("Start MLflow UI (localhost:5000)"):
        try:
            subprocess.Popen(["mlflow", "ui", "--port", "5000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            st.success("MLflow UI started on http://localhost:5000")
        except Exception as e:
            st.error(f"Failed to start MLflow UI: {e}")
with col_b:
    if st.button("Show MLflow Runs"):
        try:
            client = MlflowClient()
            exp = client.get_experiment_by_name("ai_guardian_experiments")
            if exp is None:
                st.info("No MLflow experiment found yet.")
            else:
                runs = client.search_runs(exp.experiment_id, order_by=["metrics.test_accuracy DESC"], max_results=50)
                rows = []
                for r in runs:
                    rows.append({
                        "run_id": r.info.run_id,
                        "start_time": r.info.start_time,
                        "val_acc": r.data.metrics.get("val_accuracy"),
                        "test_acc": r.data.metrics.get("test_accuracy"),
                        "test_f1": r.data.metrics.get("test_f1"),
                    })
                st.dataframe(pd.DataFrame(rows))
        except Exception as e:
            st.error(f"MLflow error: {e}")

# Promote selected run to Model Registry
st.divider()
st.header("Promote MLflow Run to Registry")
try:
    client = MlflowClient()
    exp = client.get_experiment_by_name("ai_guardian_experiments")
    if exp is None:
        st.info("No MLflow experiment found yet. Run training or sweeps to generate runs.")
    else:
        runs = client.search_runs(exp.experiment_id, order_by=["metrics.test_accuracy DESC"], max_results=100)
        if len(runs) == 0:
            st.info("No runs available in MLflow experiment.")
        else:
            run_map = {f"{r.info.run_id} (test_acc={r.data.metrics.get('test_accuracy')})": r.info.run_id for r in runs}
            selected_key = st.selectbox("Select run to promote", list(run_map.keys()))
            model_name = st.text_input("Model name", value="ai_guardian_model")
            stage = st.selectbox("Stage", ["Staging", "Production", "None"])
            if st.button("Request promotion"):
                run_id = run_map[selected_key]
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO model_promotions(model_name, version, run_id, requested_by, requested_stage, status)
                    VALUES(?,?,?,?,?,?)
                    """,
                    (model_name, None, run_id, "web_user", stage, "pending"),
                )
                conn.commit()
                conn.close()
                log("web_user", f"Requested promotion for run {run_id} as {model_name} to {stage}")
                st.success("Promotion request submitted. Approvers can review in the Approvals panel.")

            # Approvals panel
            st.divider()
            st.subheader("Approvals")
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, model_name, run_id, requested_stage, status, requested_by, created_at FROM model_promotions WHERE status='pending' ORDER BY created_at DESC")
            pending = cur.fetchall()
            conn.close()
            if not pending:
                st.info("No pending promotion requests.")
            else:
                for r in pending:
                    cid = r[0]
                    mname = r[1]
                    rrid = r[2]
                    rstage = r[3]
                    ruser = r[5]
                    created = r[6]
                    st.markdown(f"**Request {cid}** — {mname} from run {rrid} requested by {ruser} at {created} to {rstage}")
                    cols = st.columns(3)
                    if cols[0].button(f"Approve {cid}"):
                        try:
                            client.create_registered_model(mname)
                        except Exception:
                            pass
                        mv = client.create_model_version(name=mname, source=f"runs:/{rrid}/model", run_id=rrid)
                        if rstage != "None":
                            client.transition_model_version_stage(name=mname, version=mv.version, stage=rstage)
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE model_promotions SET status=?, approved_by=?, approved_at=?, version=? WHERE id=?", ("approved", "approver_user", int(time.time()), mv.version, cid))
                        conn.commit()
                        conn.close()
                        log("approver_user", f"Approved promotion {cid} -> model {mname} v{mv.version} to {rstage}")
                        st.success(f"Approved and promoted: {mname} v{mv.version} to {rstage}")
                    if cols[1].button(f"Deny {cid}"):
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE model_promotions SET status=? WHERE id=?", ("denied", cid))
                        conn.commit()
                        conn.close()
                        log("approver_user", f"Denied promotion {cid}")
                        st.info(f"Denied promotion {cid}")
                    if cols[2].button(f"View {cid}"):
                        st.write(dict(r))
except Exception as e:
    st.error(f"MLflow registry error: {e}")

if run_train:
    if not target:
        st.error("Select a target column first")
    else:
        cmd = ["python3", "scripts/train.py", "--data", str(selected), "--target", target, "--val-size", str(val_size), "--test-size", str(test_size), "--results-out", "results"]
        output.code("Running: " + " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True)
        output.code(proc.stdout + "\n" + proc.stderr)
        st.success("Training finished")

if run_sweep:
    if not target:
        st.error("Select a target column first")
    else:
        cmd = ["python3", "scripts/sweep.py", "--data", str(selected), "--target", target, "--trials", str(trials), "--results-out", "results"]
        output.code("Running: " + " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True)
        output.code(proc.stdout + "\n" + proc.stderr)
        st.success("Sweep finished")

# show leaderboard
if (results_path / "leaderboard.csv").exists():
    st.header("Leaderboard")
    lb = pd.read_csv(results_path / "leaderboard.csv")
    lb = lb.sort_values(by=["test_accuracy" if "test_accuracy" in lb.columns else "accuracy"], ascending=False)
    st.dataframe(lb)

# allow downloading latest model
models = sorted(Path("results").glob("*.joblib"), key=lambda p: p.stat().st_mtime, reverse=True)
if models:
    latest = models[0]
    st.download_button("Download latest model", data=latest.read_bytes(), file_name=latest.name)
