import streamlit as st
import pandas as pd
import os
import shutil
from pathlib import Path

from database.database import get_connection
from database.logger import log

# ----------------------------------------------------
# Page Config
# ----------------------------------------------------

st.set_page_config(

    page_title="Model Registry",

    page_icon="🤖",

    layout="wide"

)

st.title("🤖 AI Model Registry")

st.caption(

    "Register and manage machine learning models."

)

st.divider()

# ----------------------------------------------------
# Directories
# ----------------------------------------------------

MODEL_DIR = Path("models")

MODEL_DIR.mkdir(

    exist_ok=True

)

# ----------------------------------------------------
# Database
# ----------------------------------------------------

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""

SELECT

id,

name

FROM projects

ORDER BY created_at DESC

""")

projects = cursor.fetchall()

if len(projects) == 0:

    st.warning(

        "Create a project before registering models."

    )

    st.stop()

project_map = {

    row["name"]: row["id"]

    for row in projects

}

# ----------------------------------------------------
# Registration Form
# ----------------------------------------------------

st.header("Register Model")

project_name = st.selectbox(

    "Project",

    list(project_map.keys())

)

project_id = project_map[project_name]

model_name = st.text_input(

    "Model Name"

)

version = st.text_input(

    "Version",

    value="1.0.0"

)

framework = st.selectbox(

    "Framework",

    [

        "Scikit-Learn",

        "TensorFlow",

        "PyTorch",

        "XGBoost",

        "LightGBM",

        "CatBoost",

        "ONNX",

        "Other"

    ]

)

accuracy = st.number_input(

    "Accuracy (%)",

    min_value=0.0,

    max_value=100.0,

    value=90.0,

    step=0.1

)

uploaded_model = st.file_uploader(

    "Upload Model",

    type=[

        "pkl",

        "joblib",

        "onnx",

        "pt",

        "pth",

        "h5",

        "keras"

    ]

)
# ----------------------------------------------------
# Save Model
# ----------------------------------------------------

if st.button(

    "🚀 Register Model",

    type="primary"

):

    if uploaded_model is None:

        st.error(

            "Upload a model file."

        )

    elif model_name.strip() == "":

        st.error(

            "Enter a model name."

        )

    else:

        save_path = MODEL_DIR / uploaded_model.name

        with open(

            save_path,

            "wb"

        ) as f:

            shutil.copyfileobj(

                uploaded_model,

                f

            )

        cursor.execute("""

        INSERT INTO models(

            project_id,

            model_name,

            version,

            framework,

            accuracy,

            fairness,

            privacy,

            explainability,

            compliance,

            model_path

        )

        VALUES(

            ?,?,?,?,?,?,?,?,?,?

        )

        """,(

            project_id,

            model_name,

            version,

            framework,

            accuracy,

            0,

            0,

            0,

            0,

            str(save_path)

        ))

        conn.commit()

        log(

            "Developer",

            f"Registered model '{model_name}'",

            "INFO"

        )

        st.success(

            "Model registered successfully."

        )

        st.balloons()

st.divider()
# ----------------------------------------------------
# Registered Models
# ----------------------------------------------------

st.header("Registered Models")

cursor.execute("""

SELECT

m.id,

p.name,

m.model_name,

m.version,

m.framework,

m.accuracy,

m.fairness,

m.privacy,

m.explainability

FROM models m

JOIN projects p

ON p.id=m.project_id

ORDER BY m.uploaded_at DESC

""")

rows = cursor.fetchall()

conn.close()

if len(rows) == 0:

    st.info(

        "No registered models."

    )

else:

    df = pd.DataFrame(

        rows,

        columns=[

            "ID",

            "Project",

            "Model",

            "Version",

            "Framework",

            "Accuracy",

            "Fairness",

            "Privacy",

            "Explainability"

        ]

    )

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )

    st.metric(

        "Registered Models",

        len(df)

    )