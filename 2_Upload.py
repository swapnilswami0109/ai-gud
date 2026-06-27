import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------

st.set_page_config(
    page_title="Upload & Analyze Dataset",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Dataset Upload & Analysis")

st.write(
    "Upload a dataset file and review key statistics, quality metrics, missing values, duplicate rows, and sample data."
)


@st.cache_data

def load_dataset(uploaded_file):
    suffix = uploaded_file.name.split(".")[-1].lower()
    if suffix == "csv":
        return pd.read_csv(uploaded_file)
    if suffix in ["xlsx", "xls"]:
        return pd.read_excel(uploaded_file)
    if suffix == "json":
        return pd.read_json(uploaded_file)
    raise ValueError("Unsupported file type. Upload CSV, Excel, or JSON.")


def dataset_statistics(df: pd.DataFrame) -> dict:
    return {
        "Rows": int(df.shape[0]),
        "Columns": int(df.shape[1]),
        "Missing Values": int(df.isnull().sum().sum()),
        "Duplicate Rows": int(df.duplicated().sum()),
        "Memory (KB)": int(df.memory_usage(deep=True).sum() / 1024)
    }


def compute_quality_score(stats: dict) -> float:
    score = 100.0
    score -= min(stats["Missing Values"], 200) * 0.15
    score -= min(stats["Duplicate Rows"], 100) * 0.25
    return max(round(score, 2), 0.0)


uploaded_file = st.file_uploader(
    "Upload dataset",
    type=["csv", "xlsx", "xls", "json"],
    help="Supported file types: CSV, Excel, JSON"
)

if uploaded_file is None:
    st.info("Please upload a dataset file to begin analysis.")
    st.stop()

try:
    dataframe = load_dataset(uploaded_file)
except Exception as error:
    st.error(f"Failed to load dataset: {error}")
    st.stop()

stats = dataset_statistics(dataframe)

st.success("Dataset loaded successfully.")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Rows", stats["Rows"])

c2.metric("Columns", stats["Columns"])

c3.metric("Missing", stats["Missing Values"])

c4.metric("Duplicates", stats["Duplicate Rows"])

c5.metric("Memory", f"{stats['Memory (KB)']} KB")

st.divider()

st.subheader("Dataset Preview")

preview_rows = st.slider(
    "Rows to preview",
    min_value=5,
    max_value=min(100, stats["Rows"] if stats["Rows"] > 0 else 100),
    value=min(10, stats["Rows"] if stats["Rows"] > 0 else 10)
)

st.dataframe(dataframe.head(preview_rows), use_container_width=True)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Column Information")
    info_df = pd.DataFrame({
        "Column": dataframe.columns.astype(str),
        "Data Type": dataframe.dtypes.astype(str),
        "Missing": dataframe.isnull().sum().values,
        "Unique": dataframe.nunique().values,
    })
    st.dataframe(info_df, use_container_width=True, hide_index=True)

with right:
    st.subheader("Numeric Summary")
    numeric = dataframe.select_dtypes(include=["number"])
    if numeric.shape[1] > 0:
        st.dataframe(numeric.describe().T, use_container_width=True)
    else:
        st.info("No numeric columns found.")

st.divider()

st.subheader("Missing Value Analysis")

missing_df = dataframe.isnull().sum().reset_index()
missing_df.columns = ["Column", "Missing Values"]

st.dataframe(missing_df, use_container_width=True, hide_index=True)

if len(missing_df) > 0:
    missing_chart = px.bar(
        missing_df,
        x="Column",
        y="Missing Values",
        title="Missing Values by Column",
    )
    missing_chart.update_layout(xaxis_title=None, yaxis_title="Missing Values")
    st.plotly_chart(missing_chart, use_container_width=True)

st.divider()

st.subheader("Duplicate Row Analysis")

duplicate_rows = dataframe[dataframe.duplicated()]

st.write(f"Total duplicate rows: **{len(duplicate_rows)}**")

if len(duplicate_rows) > 0:
    st.dataframe(duplicate_rows.head(50), use_container_width=True)
else:
    st.success("No duplicate rows detected.")

st.divider()

quality_score = compute_quality_score(stats)

st.subheader("Dataset Quality Score")

st.progress(quality_score / 100)

st.metric("Quality Score", f"{quality_score}%")

if quality_score >= 90:
    st.success("Excellent dataset quality.")
elif quality_score >= 75:
    st.warning("Dataset quality is acceptable.")
else:
    st.error("Dataset requires cleaning.")

st.divider()

st.header("Export Dataset")

csv_data = dataframe.to_csv(index=False).encode("utf-8")

st.download_button("📥 Download CSV", csv_data, "dataset_export.csv", "text/csv")
