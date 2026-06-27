import streamlit as st
import pandas as pd

from pathlib import Path

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------

st.set_page_config(

    page_title="Privacy Scanner",

    page_icon="🔒",

    layout="wide"

)

st.title("🔒 Privacy Scanner")

st.caption(

    "Detect Personally Identifiable Information (PII) using Microsoft Presidio"

)

st.divider()

# -----------------------------------------------------
# Load Dataset
# -----------------------------------------------------

UPLOAD_DIR = Path("uploads")

files = sorted(

    UPLOAD_DIR.glob("*")

)

if len(files) == 0:

    st.warning(

        "No uploaded datasets found."

    )

    st.stop()

selected = st.selectbox(

    "Dataset",

    files,

    format_func=lambda x: x.name

)

suffix = selected.suffix.lower()

try:

    if suffix == ".csv":

        df = pd.read_csv(selected)

    elif suffix in [".xlsx", ".xls"]:

        df = pd.read_excel(selected)

    elif suffix == ".json":

        df = pd.read_json(selected)

    else:

        st.error("Unsupported file.")

        st.stop()

except Exception as e:

    st.error(e)

    st.stop()

st.success("Dataset loaded.")

st.dataframe(

    df.head(),

    use_container_width=True

)

st.divider()

# -----------------------------------------------------
# Initialize Presidio
# -----------------------------------------------------

analyzer = AnalyzerEngine()

anonymizer = AnonymizerEngine()

# -----------------------------------------------------
# Select Columns
# -----------------------------------------------------

text_columns = [

    c

    for c in df.columns

    if df[c].dtype == object

]

if len(text_columns) == 0:

    st.warning(

        "No text columns found."

    )

    st.stop()

selected_columns = st.multiselect(

    "Columns to Scan",

    text_columns,

    default=text_columns

)

st.divider()

# -----------------------------------------------------
# Scan Button
# -----------------------------------------------------

scan = st.button(

    "🔍 Scan Dataset",

    type="primary"

)

if not scan:

    st.stop()
    # -----------------------------------------------------
# Scan Dataset
# -----------------------------------------------------

results = []

total_records = 0

progress = st.progress(0)

status = st.empty()

for column in selected_columns:

    values = df[column].fillna("").astype(str)

    total = len(values)

    for index, text in enumerate(values):

        if text.strip() == "":

            continue

        entities = analyzer.analyze(

            text=text,

            language="en"

        )

        total_records += 1

        for entity in entities:

            results.append({

                "Row": index,

                "Column": column,

                "Entity": entity.entity_type,

                "Score": round(

                    entity.score,

                    3

                ),

                "Text": text[:100]

            })

        progress.progress(

            (index + 1) / total

        )

        status.info(

            f"Scanning {column} ({index+1}/{total})"

        )

status.empty()

progress.empty()

# -----------------------------------------------------
# Results
# -----------------------------------------------------

st.header("PII Detection Results")

if len(results) == 0:

    st.success(

        "No Personally Identifiable Information detected."

    )

    st.stop()

results_df = pd.DataFrame(results)

st.dataframe(

    results_df,

    use_container_width=True,

    hide_index=True

)

st.divider()

# -----------------------------------------------------
# Entity Counts
# -----------------------------------------------------

st.subheader("Detected Entity Types")

entity_counts = (

    results_df

    .groupby("Entity")

    .size()

    .reset_index(name="Count")

)

st.dataframe(

    entity_counts,

    use_container_width=True,

    hide_index=True

)

st.bar_chart(

    entity_counts.set_index(

        "Entity"

    )

)

st.divider()

# -----------------------------------------------------
# Risk Score
# -----------------------------------------------------

total_cells = len(df) * len(selected_columns)

detected = len(results_df)

risk = round(

    min(

        (detected / max(total_cells, 1)) * 100,

        100

    ),

    2

)

c1, c2, c3 = st.columns(3)

c1.metric(

    "Records Scanned",

    total_records

)

c2.metric(

    "PII Detected",

    detected

)

c3.metric(

    "Privacy Risk",

    f"{risk}%"

)

if risk < 10:

    st.success(

        "Low Privacy Risk"

    )

elif risk < 30:

    st.warning(

        "Medium Privacy Risk"

    )

else:

    st.error(

        "High Privacy Risk"

    )

st.divider()

# -----------------------------------------------------
# Entity Distribution
# -----------------------------------------------------

st.subheader("Entity Distribution")

distribution = (

    results_df

    .groupby("Entity")

    .size()

    .sort_values(

        ascending=False

    )

)

st.bar_chart(

    distribution

)