import io
import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import get_connection

# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------

st.set_page_config(

    page_title="AI Governance Dashboard",

    page_icon="🏛️",

    layout="wide"

)

st.title("🏛️ AI Governance Dashboard")

st.caption(

    "Enterprise Responsible AI Governance Overview"

)

st.divider()

# -----------------------------------------------------
# Database Connection
# -----------------------------------------------------

conn = get_connection()

cursor = conn.cursor()

# -----------------------------------------------------
# Load Projects
# -----------------------------------------------------

cursor.execute("""

SELECT *

FROM projects

ORDER BY created_at DESC

""")

projects = cursor.fetchall()

projects_df = pd.DataFrame(

    projects,

    columns=projects[0].keys()

) if projects else pd.DataFrame()

# -----------------------------------------------------
# Load Models
# -----------------------------------------------------

cursor.execute("""

SELECT *

FROM models

ORDER BY uploaded_at DESC

""")

models = cursor.fetchall()

models_df = pd.DataFrame(

    models,

    columns=models[0].keys()

) if models else pd.DataFrame()

# -----------------------------------------------------
# Load Certificates
# -----------------------------------------------------

cursor.execute("""

SELECT *

FROM certificates

ORDER BY issued_at DESC

""")

certificates = cursor.fetchall()

certificates_df = pd.DataFrame(

    certificates,

    columns=certificates[0].keys()

) if certificates else pd.DataFrame()

# -----------------------------------------------------
# Load Audit Logs
# -----------------------------------------------------

cursor.execute("""

SELECT *

FROM audit_logs

ORDER BY created_at DESC

LIMIT 20

""")

logs = cursor.fetchall()

logs_df = pd.DataFrame(

    logs,

    columns=logs[0].keys()

) if logs else pd.DataFrame()

conn.close()

# -----------------------------------------------------
# KPI Cards
# -----------------------------------------------------

st.header("Organization Overview")

projects_count = len(projects_df)

models_count = len(models_df)

certificates_count = len(certificates_df)

if not models_df.empty:

    avg_fairness = round(

        models_df["fairness"].fillna(0).mean(),

        2

    )

    avg_privacy = round(

        models_df["privacy"].fillna(0).mean(),

        2

    )

    avg_explainability = round(

        models_df["explainability"].fillna(0).mean(),

        2

    )

else:

    avg_fairness = 0

    avg_privacy = 0

    avg_explainability = 0

overall_score = round(

    (

        avg_fairness +

        avg_privacy +

        avg_explainability

    ) / 3,

    2

)

k1, k2, k3, k4 = st.columns(4)

k1.metric(

    "Projects",

    projects_count

)

k2.metric(

    "Models",

    models_count

)

k3.metric(

    "Certificates",

    certificates_count

)

k4.metric(

    "Compliance",

    f"{overall_score}%"

)

st.progress(

    overall_score / 100

)

st.divider()
# -----------------------------------------------------
# Compliance Overview
# -----------------------------------------------------

st.header("Compliance Overview")

if models_df.empty:

    st.info("No model analysis available.")

else:

    compliance_df = pd.DataFrame({

        "Metric":[

            "Fairness",

            "Privacy",

            "Explainability"

        ],

        "Average Score":[

            avg_fairness,

            avg_privacy,

            avg_explainability

        ]

    })

    c1, c2 = st.columns(2)

    with c1:

        fig = px.bar(

            compliance_df,

            x="Metric",

            y="Average Score",

            text="Average Score",

            color="Metric",

            title="Average Responsible AI Scores"

        )

        fig.update_layout(

            height=450,

            showlegend=False

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    with c2:

        fig = px.pie(

            compliance_df,

            names="Metric",

            values="Average Score",

            title="Compliance Distribution"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

st.divider()

# -----------------------------------------------------
# Project Comparison
# -----------------------------------------------------

st.header("Project Comparison")

if models_df.empty:

    st.info("No projects available.")

else:

    comparison = models_df[[

        "project_id",

        "fairness",

        "privacy",

        "explainability"

    ]].fillna(0)

    st.dataframe(

        comparison,

        use_container_width=True,

        hide_index=True

    )

    fig = px.bar(

        comparison,

        x="project_id",

        y=[

            "fairness",

            "privacy",

            "explainability"

        ],

        barmode="group",

        title="Project Responsible AI Scores"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

st.divider()

# -----------------------------------------------------
# Risk Distribution
# -----------------------------------------------------

st.header("Risk Distribution")

if not models_df.empty:

    risk_levels = []

    for _, row in models_df.iterrows():

        score = (

            row["fairness"] +

            row["privacy"] +

            row["explainability"]

        ) / 3

        if score >= 90:

            risk_levels.append("Low")

        elif score >= 75:

            risk_levels.append("Medium")

        else:

            risk_levels.append("High")

    risk_df = pd.DataFrame({

        "Risk": risk_levels

    })

    risk_summary = (

        risk_df

        .groupby("Risk")

        .size()

        .reset_index(name="Projects")

    )

    fig = px.pie(

        risk_summary,

        names="Risk",

        values="Projects",

        title="Project Risk Levels"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

st.divider()

# -----------------------------------------------------
# Certificate Statistics
# -----------------------------------------------------

st.header("Certificates")

if certificates_df.empty:

    st.info("No certificates issued.")

else:

    st.metric(

        "Certificates Issued",

        len(certificates_df)

    )

    st.dataframe(

        certificates_df,

        use_container_width=True,

        hide_index=True

    )

st.divider()

# -----------------------------------------------------
# Recent Audit Logs
# -----------------------------------------------------

st.header("Recent Audit Activity")

if logs_df.empty:

    st.info("No audit logs available.")

else:

    st.dataframe(

        logs_df,

        use_container_width=True,

        hide_index=True

    )

st.divider()
# -----------------------------------------------------
# Executive Scorecard
# -----------------------------------------------------

st.header("Executive Scorecard")

scorecard = pd.DataFrame({

    "Metric":[

        "Projects",

        "Models",

        "Certificates",

        "Average Fairness",

        "Average Privacy",

        "Average Explainability",

        "Overall Compliance"

    ],

    "Value":[

        projects_count,

        models_count,

        certificates_count,

        avg_fairness,

        avg_privacy,

        avg_explainability,

        overall_score

    ]

})

st.dataframe(

    scorecard,

    use_container_width=True,

    hide_index=True

)

st.divider()

# -----------------------------------------------------
# Governance Status
# -----------------------------------------------------

st.header("Governance Status")

if overall_score >= 90:

    status = "Excellent"

    st.success(

        "🟢 Enterprise AI Governance is operating within recommended thresholds."

    )

elif overall_score >= 75:

    status = "Good"

    st.warning(

        "🟡 Governance is acceptable but improvements are recommended."

    )

else:

    status = "Needs Improvement"

    st.error(

        "🔴 Governance posture requires immediate attention."

    )

st.metric(

    "Governance Status",

    status

)

st.divider()

# -----------------------------------------------------
# Governance Recommendations
# -----------------------------------------------------

st.header("Recommendations")

recommendations = []

if avg_fairness < 80:

    recommendations.append(

        "Improve fairness by reducing demographic disparities and validating training datasets."

    )

if avg_privacy < 80:

    recommendations.append(

        "Strengthen privacy protections through anonymization and secure data handling."

    )

if avg_explainability < 80:

    recommendations.append(

        "Increase model transparency by expanding explainability analysis."

    )

if overall_score < 90:

    recommendations.append(

        "Schedule periodic Responsible AI reviews for all active projects."

    )

if recommendations:

    for rec in recommendations:

        st.warning(rec)

else:

    st.success(

        "No major governance concerns detected."

    )

st.divider()

# -----------------------------------------------------
# Search Projects
# -----------------------------------------------------

st.header("Project Search")

if not projects_df.empty:

    search = st.text_input(

        "Search by Project Name"

    )

    filtered = projects_df.copy()

    if search:

        filtered = filtered[

            filtered["name"].astype(str).str.contains(

                search,

                case=False,

                na=False

            )

        ]

    st.dataframe(

        filtered,

        use_container_width=True,

        hide_index=True

    )

st.divider()

# -----------------------------------------------------
# Export Dashboard
# -----------------------------------------------------

st.header("Export Dashboard")

buffer = io.BytesIO()

with pd.ExcelWriter(

    buffer,

    engine="openpyxl"

) as writer:

    scorecard.to_excel(

        writer,

        sheet_name="Executive Scorecard",

        index=False

    )

    if not projects_df.empty:

        projects_df.to_excel(

            writer,

            sheet_name="Projects",

            index=False

        )

    if not models_df.empty:

        models_df.to_excel(

            writer,

            sheet_name="Models",

            index=False

        )

    if not certificates_df.empty:

        certificates_df.to_excel(

            writer,

            sheet_name="Certificates",

            index=False

        )

    if not logs_df.empty:

        logs_df.to_excel(

            writer,

            sheet_name="Audit Logs",

            index=False

        )

st.download_button(

    "⬇ Download Governance Dashboard",

    buffer.getvalue(),

    "governance_dashboard.xlsx",

    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)

st.divider()

# -----------------------------------------------------
# Executive Summary
# -----------------------------------------------------

st.header("Executive Summary")

summary = f"""
AI Guardian OS Governance Overview

Projects Managed : {projects_count}

Registered Models : {models_count}

Certificates Issued : {certificates_count}

Average Fairness : {avg_fairness:.2f}%

Average Privacy : {avg_privacy:.2f}%

Average Explainability : {avg_explainability:.2f}%

Overall Compliance : {overall_score:.2f}%

Governance Status : {status}

The organization can use this dashboard
to monitor Responsible AI maturity,
identify risk areas, and support
regulatory reporting.
"""

st.info(summary)

st.divider()

# -----------------------------------------------------
# Footer
# -----------------------------------------------------

st.success(

    """
AI Governance Dashboard loaded successfully.

All metrics shown are aggregated from the
current AI Guardian OS database.
"""
)