import streamlit as st
import pandas as pd

from database.database import get_connection
from database.logger import log

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(

    page_title="AI Risk Register",

    page_icon="⚠️",

    layout="wide"

)

st.title("⚠️ AI Risk Register")

st.caption(

    "Track AI governance risks across projects."

)

st.divider()

# ----------------------------------------------------
# Database
# ----------------------------------------------------

conn = get_connection()

cursor = conn.cursor()

# ----------------------------------------------------
# Create Table
# ----------------------------------------------------

cursor.execute("""

CREATE TABLE IF NOT EXISTS risk_register(

id INTEGER PRIMARY KEY AUTOINCREMENT,

project_id INTEGER,

risk_name TEXT,

category TEXT,

severity TEXT,

likelihood TEXT,

owner TEXT,

status TEXT,

mitigation TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

""")

conn.commit()

# ----------------------------------------------------
# Load Projects
# ----------------------------------------------------

cursor.execute("""

SELECT id,name

FROM projects

ORDER BY created_at DESC

""")

projects = cursor.fetchall()

if len(projects)==0:

    st.warning(

        "Create a project first."

    )

    conn.close()

    st.stop()

project_map={

    p["name"]:p["id"]

    for p in projects

}

# ----------------------------------------------------
# Risk Form
# ----------------------------------------------------

st.header("Create Risk")

project=st.selectbox(

    "Project",

    list(project_map.keys())

)

project_id=project_map[project]

risk_name=st.text_input(

    "Risk Name"

)

category=st.selectbox(

    "Category",

    [

        "Bias",

        "Privacy",

        "Security",

        "Compliance",

        "Explainability",

        "Model Drift",

        "Data Quality",

        "Operational"

    ]

)

severity=st.selectbox(

    "Severity",

    [

        "Low",

        "Medium",

        "High",

        "Critical"

    ]

)

likelihood=st.selectbox(

    "Likelihood",

    [

        "Rare",

        "Possible",

        "Likely",

        "Almost Certain"

    ]

)

owner=st.text_input(

    "Risk Owner"

)

status=st.selectbox(

    "Status",

    [

        "Open",

        "In Progress",

        "Mitigated",

        "Closed"

    ]

)

mitigation=st.text_area(

    "Mitigation Plan"
)
import io
import plotly.express as px

# ----------------------------------------------------
# Risk Dashboard
# ----------------------------------------------------

st.header("📊 Risk Dashboard")

if len(risk_df) == 0:

    st.info("No risks available for analysis.")

    st.stop()

# ----------------------------------------------------
# Risk Score Mapping
# ----------------------------------------------------

severity_score = {

    "Low": 1,

    "Medium": 2,

    "High": 3,

    "Critical": 4

}

likelihood_score = {

    "Rare": 1,

    "Possible": 2,

    "Likely": 3,

    "Almost Certain": 4

}

dashboard = risk_df.copy()

dashboard["Severity Score"] = dashboard["Severity"].map(

    severity_score

)

dashboard["Likelihood Score"] = dashboard["Likelihood"].map(

    likelihood_score

)

dashboard["Risk Score"] = (

    dashboard["Severity Score"] *

    dashboard["Likelihood Score"]

)

# ----------------------------------------------------
# KPI Cards
# ----------------------------------------------------

total_risks = len(dashboard)

critical = len(

    dashboard[

        dashboard["Severity"] == "Critical"

    ]

)

open_risks = len(

    dashboard[

        dashboard["Status"] == "Open"

    ]

)

avg_score = round(

    dashboard["Risk Score"].mean(),

    2

)

k1, k2, k3, k4 = st.columns(4)

k1.metric(

    "Total Risks",

    total_risks

)

k2.metric(

    "Critical",

    critical

)

k3.metric(

    "Open",

    open_risks

)

k4.metric(

    "Average Score",

    avg_score

)

st.divider()

# ----------------------------------------------------
# Risk Matrix
# ----------------------------------------------------

st.header("Risk Matrix")

matrix = px.scatter(

    dashboard,

    x="Likelihood Score",

    y="Severity Score",

    color="Category",

    size="Risk Score",

    hover_name="Risk",

    text="Risk",

    title="Risk Heatmap"

)

matrix.update_layout(

    xaxis=dict(

        tickvals=[1,2,3,4],

        ticktext=[

            "Rare",

            "Possible",

            "Likely",

            "Almost Certain"

        ]

    ),

    yaxis=dict(

        tickvals=[1,2,3,4],

        ticktext=[

            "Low",

            "Medium",

            "High",

            "Critical"

        ]

    ),

    height=600

)

st.plotly_chart(

    matrix,

    use_container_width=True

)

st.divider()

# ----------------------------------------------------
# Risks by Category
# ----------------------------------------------------

st.header("Category Distribution")

category = (

    dashboard

    .groupby("Category")

    .size()

    .reset_index(name="Count")

)

fig = px.bar(

    category,

    x="Category",

    y="Count",

    text="Count",

    color="Category"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ----------------------------------------------------
# Severity Distribution
# ----------------------------------------------------

st.header("Severity Distribution")

severity = (

    dashboard

    .groupby("Severity")

    .size()

    .reset_index(name="Count")

)

fig = px.pie(

    severity,

    names="Severity",

    values="Count"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()
# ----------------------------------------------------
# Search & Filter
# ----------------------------------------------------

st.header("🔍 Search & Filter Risks")

c1, c2 = st.columns(2)

with c1:

    search = st.text_input(

        "Search Risk"

    )

with c2:

    status_filter = st.selectbox(

        "Status Filter",

        [

            "All",

            "Open",

            "In Progress",

            "Mitigated",

            "Closed"

        ]

    )

filtered = dashboard.copy()

if search:

    filtered = filtered[

        filtered["Risk"]

        .astype(str)

        .str.contains(

            search,

            case=False,

            na=False

        )

    ]

if status_filter != "All":

    filtered = filtered[

        filtered["Status"] == status_filter

    ]

st.dataframe(

    filtered,

    use_container_width=True,

    hide_index=True

)

st.divider()

# ----------------------------------------------------
# Update Risk Status
# ----------------------------------------------------

st.header("✏️ Update Risk Status")

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""

SELECT

id,

risk_name

FROM risk_register

ORDER BY created_at DESC

""")

risk_records = cursor.fetchall()

if risk_records:

    risk_lookup = {

        f"{r['id']} - {r['risk_name']}": r["id"]

        for r in risk_records

    }

    selected_risk = st.selectbox(

        "Select Risk",

        list(risk_lookup.keys())

    )

    new_status = st.selectbox(

        "New Status",

        [

            "Open",

            "In Progress",

            "Mitigated",

            "Closed"

        ],

        key="update_status"

    )

    if st.button(

        "✅ Update Status"

    ):

        cursor.execute(

            """

            UPDATE risk_register

            SET status=?

            WHERE id=?

            """,

            (

                new_status,

                risk_lookup[selected_risk]

            )

        )

        conn.commit()

        log(

            "Developer",

            f"Updated risk {risk_lookup[selected_risk]} to {new_status}",

            "INFO"

        )

        st.success(

            "Risk updated successfully."

        )

conn.close()

st.divider()

# ----------------------------------------------------
# Executive Recommendations
# ----------------------------------------------------

st.header("📋 Governance Recommendations")

recommendations = []

if critical > 0:

    recommendations.append(

        "Immediately review all Critical risks and assign mitigation owners."

    )

if open_risks > 5:

    recommendations.append(

        "Reduce the number of open risks through prioritization and action plans."

    )

if avg_score >= 9:

    recommendations.append(

        "Overall organizational AI risk is high. Schedule a governance review."

    )

if not recommendations:

    st.success(

        "Current AI risk posture is within acceptable limits."

    )

else:

    for rec in recommendations:

        st.warning(rec)

st.divider()

# ----------------------------------------------------
# Export Risk Register
# ----------------------------------------------------

st.header("📥 Export Risk Register")

buffer = io.BytesIO()

with pd.ExcelWriter(

    buffer,

    engine="openpyxl"

) as writer:

    dashboard.to_excel(

        writer,

        sheet_name="Risk Register",

        index=False

    )

st.download_button(

    "⬇ Download Excel",

    buffer.getvalue(),

    "ai_risk_register.xlsx",

    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)

csv = dashboard.to_csv(

    index=False

).encode("utf-8")

st.download_button(

    "⬇ Download CSV",

    csv,

    "ai_risk_register.csv",

    "text/csv"

)

st.divider()

# ----------------------------------------------------
# Executive Summary
# ----------------------------------------------------

st.header("📈 Executive Summary")

summary = f"""
AI Risk Register Summary

Total Risks: {total_risks}

Critical Risks: {critical}

Open Risks: {open_risks}

Average Risk Score: {avg_score}

The current register provides a centralized
view of Responsible AI risks across projects.
Regular reviews and mitigation activities
should be conducted to maintain compliance.
"""

st.info(summary)

st.divider()

# ----------------------------------------------------
# Refresh Dashboard
# ----------------------------------------------------

if st.button(

    "🔄 Refresh"

):

    st.rerun()

st.success(

    "AI Risk Register loaded successfully."
)