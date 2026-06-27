import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from database.database import get_connection
from database.logger import log

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(

    page_title="Live Model Monitoring",

    page_icon="📡",

    layout="wide"

)

st.title("📡 Live Model Monitoring")

st.caption(

    "Monitor AI model health and Responsible AI metrics."

)

st.divider()

# ----------------------------------------------------
# Database
# ----------------------------------------------------

conn = get_connection()

cursor = conn.cursor()

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

m.explainability,

m.compliance

FROM models m

JOIN projects p

ON p.id = m.project_id

ORDER BY m.uploaded_at DESC

""")

rows = cursor.fetchall()

if len(rows) == 0:

    st.warning(

        "No registered models found."

    )

    conn.close()

    st.stop()

models_df = pd.DataFrame(

    rows,

    columns=[

        "Model ID",

        "Project",

        "Model",

        "Version",

        "Framework",

        "Accuracy",

        "Fairness",

        "Privacy",

        "Explainability",

        "Compliance"

    ]

)

# ----------------------------------------------------
# Model Selection
# ----------------------------------------------------

selected_model = st.selectbox(

    "Select Model",

    models_df["Model"]

)

current = models_df[

    models_df["Model"] == selected_model

].iloc[0]

# ----------------------------------------------------
# KPI Dashboard
# ----------------------------------------------------

st.header("Current Metrics")

k1, k2, k3, k4 = st.columns(4)

k1.metric(

    "Accuracy",

    f"{current['Accuracy']:.2f}%"

)

k2.metric(

    "Fairness",

    f"{current['Fairness']:.2f}%"

)

k3.metric(

    "Privacy",

    f"{current['Privacy']:.2f}%"

)

k4.metric(

    "Explainability",

    f"{current['Explainability']:.2f}%"

)

st.divider()

# ----------------------------------------------------
# Health Score
# ----------------------------------------------------

health = round(

    (

        current["Accuracy"] +

        current["Fairness"] +

        current["Privacy"] +

        current["Explainability"]

    ) / 4,

    2

)

st.subheader("Overall Model Health")

st.progress(

    health / 100

)

st.metric(

    "Health Score",

    f"{health}%"

)

if health >= 90:

    st.success("🟢 Model operating normally.")

elif health >= 75:

    st.warning("🟡 Model requires observation.")

else:

    st.error("🔴 Immediate review recommended.")

st.divider()
import numpy as np

# ----------------------------------------------------
# Simulated Historical Metrics
# ----------------------------------------------------

st.header("Performance Trends")

days = pd.date_range(

    end=datetime.today(),

    periods=30

)

np.random.seed(42)

history = pd.DataFrame({

    "Date": days,

    "Accuracy": np.clip(

        current["Accuracy"] +

        np.random.normal(0, 1.2, 30),

        0,

        100

    ),

    "Fairness": np.clip(

        current["Fairness"] +

        np.random.normal(0, 1.5, 30),

        0,

        100

    ),

    "Privacy": np.clip(

        current["Privacy"] +

        np.random.normal(0, 1.0, 30),

        0,

        100

    ),

    "Explainability": np.clip(

        current["Explainability"] +

        np.random.normal(0, 1.3, 30),

        0,

        100

    )

})

# ----------------------------------------------------
# Trend Chart
# ----------------------------------------------------

trend = history.melt(

    id_vars="Date",

    var_name="Metric",

    value_name="Score"

)

fig = px.line(

    trend,

    x="Date",

    y="Score",

    color="Metric",

    markers=True,

    title="Responsible AI Metrics Over Time"

)

fig.update_layout(

    height=550

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ----------------------------------------------------
# Current Metric Comparison
# ----------------------------------------------------

st.header("Current Metric Comparison")

comparison = pd.DataFrame({

    "Metric":[

        "Accuracy",

        "Fairness",

        "Privacy",

        "Explainability"

    ],

    "Score":[

        current["Accuracy"],

        current["Fairness"],

        current["Privacy"],

        current["Explainability"]

    ]

})

fig = px.bar(

    comparison,

    x="Metric",

    y="Score",

    text="Score",

    color="Metric",

    title="Current Responsible AI Metrics"

)

fig.update_layout(

    height=450,

    showlegend=False

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ----------------------------------------------------
# Threshold Monitoring
# ----------------------------------------------------

st.header("Threshold Monitoring")

threshold = st.slider(

    "Minimum Acceptable Score",

    min_value=50,

    max_value=100,

    value=80

)

alerts = []

for metric in [

    "Accuracy",

    "Fairness",

    "Privacy",

    "Explainability"

]:

    value = current[metric]

    if value < threshold:

        alerts.append(

            (metric, value)

        )

if len(alerts) == 0:

    st.success(

        "All monitored metrics are above the configured threshold."

    )

else:

    for metric, value in alerts:

        st.error(

            f"{metric}: {value:.2f}% is below the threshold."

        )

st.divider()

# ----------------------------------------------------
# Drift Indicator
# ----------------------------------------------------

st.header("Model Drift Indicator")

drift = round(

    abs(

        history["Accuracy"].iloc[-1] -

        history["Accuracy"].iloc[0]

    ),

    2

)

st.metric(

    "Estimated Drift",

    f"{drift}%"

)

if drift < 2:

    st.success(

        "No significant drift detected."

    )

elif drift < 5:

    st.warning(

        "Potential drift detected. Continue monitoring."

    )

else:

    st.error(

        "Significant drift detected. Retraining is recommended."

    )

st.divider()
# ----------------------------------------------------
# Operational Status
# ----------------------------------------------------

st.header("Operational Status")

status_data = pd.DataFrame({

    "Component":[

        "Model Service",

        "Bias Monitor",

        "Privacy Scanner",

        "Explainability Engine",

        "Compliance Monitor"

    ],

    "Status":[

        "Online",

        "Online",

        "Online",

        "Online",

        "Online"

    ]

})

st.dataframe(

    status_data,

    use_container_width=True,

    hide_index=True

)

st.divider()

# ----------------------------------------------------
# Monitoring Recommendations
# ----------------------------------------------------

st.header("Recommendations")

recommendations = []

if current["Accuracy"] < 80:

    recommendations.append(

        "Retrain the model to improve predictive performance."

    )

if current["Fairness"] < 80:

    recommendations.append(

        "Review fairness metrics and evaluate potential bias mitigation strategies."

    )

if current["Privacy"] < 80:

    recommendations.append(

        "Run a new privacy assessment and verify sensitive data handling."

    )

if current["Explainability"] < 80:

    recommendations.append(

        "Generate updated SHAP explanations and review feature importance."

    )

if drift >= 5:

    recommendations.append(

        "Investigate model drift and consider retraining with more recent data."

    )

if recommendations:

    for item in recommendations:

        st.warning(item)

else:

    st.success(

        "No immediate actions required."

    )

st.divider()

# ----------------------------------------------------
# Monitoring Event
# ----------------------------------------------------

st.header("Log Monitoring Event")

operator = st.text_input(

    "Operator",

    value="Developer"

)

if st.button(

    "📝 Record Monitoring Check"

):

    log(

        operator,

        f"Completed monitoring check for model '{selected_model}'",

        "INFO"

    )

    st.success(

        "Monitoring event recorded."

    )

st.divider()

# ----------------------------------------------------
# Export Monitoring Data
# ----------------------------------------------------

st.header("Export Monitoring Data")

csv_data = history.to_csv(

    index=False

).encode("utf-8")

st.download_button(

    "⬇ Download Monitoring CSV",

    csv_data,

    "model_monitoring_history.csv",

    "text/csv"

)

excel_buffer = io.BytesIO()

with pd.ExcelWriter(

    excel_buffer,

    engine="openpyxl"

) as writer:

    history.to_excel(

        writer,

        sheet_name="History",

        index=False
    )

    comparison.to_excel(

        writer,

        sheet_name="Current Metrics",

        index=False

    )

st.download_button(

    "⬇ Download Monitoring Excel",

    excel_buffer.getvalue(),

    "model_monitoring_history.xlsx",

    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)

st.divider()

# ----------------------------------------------------
# Monitoring Summary
# ----------------------------------------------------

st.header("Monitoring Summary")

summary = f"""
Monitoring completed successfully.

Model: {selected_model}

Project: {current['Project']}

Framework: {current['Framework']}

Overall Health Score: {health:.2f}%

Estimated Drift: {drift:.2f}%

Monitoring Threshold: {threshold}%

Alerts Triggered: {len(alerts)}

Review the recommendations above before deploying
new model versions or promoting this model to production.
"""

st.info(summary)

st.divider()

# ----------------------------------------------------
# Refresh
# ----------------------------------------------------

refresh = st.button(

    "🔄 Refresh Dashboard"

)

if refresh:

    st.rerun()

st.success(

    "Live Model Monitoring dashboard is ready."
)