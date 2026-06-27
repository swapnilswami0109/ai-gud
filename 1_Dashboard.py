"""Autonomic Dashboard - Executive governance visibility."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Autonomic - Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==================== HEADER ====================
st.title("🛡️ Autonomic: AI Governance Dashboard")
st.caption("Real-time trust scoring, compliance monitoring, and risk management for enterprise AI")

st.divider()

# ==================== KEY METRICS ====================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Trust Score",
        value="78/100",
        delta="+5",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Status",
        value="✅ APPROVED",
        delta="Ready for production"
    )

with col3:
    st.metric(
        label="Models Analyzed",
        value="247",
        delta="+23 this month"
    )

with col4:
    st.metric(
        label="Compliance",
        value="92%",
        delta="+3"
    )

with col5:
    st.metric(
        label="Risk Level",
        value="🟢 LOW",
        delta="No critical issues"
    )

st.divider()

# ==================== TRUST SCORE EVOLUTION ====================
st.subheader("📈 Trust Score Evolution (Last 90 Days)")

# Generate mock historical data
days = np.arange(0, 90)
trend = 50 + 20 * np.sin(days/15) + 2 * np.random.randn(90)
trend = np.clip(trend, 0, 100)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=days,
    y=trend,
    mode='lines+markers',
    name='Trust Score',
    line=dict(color='#1f77b4', width=3),
    fill='tozeroy',
    fillcolor='rgba(31, 119, 180, 0.2)'
))

fig_trend.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Approval Threshold (75)")
fig_trend.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Review Threshold (50)")

fig_trend.update_layout(
    title="",
    xaxis_title="Days Ago",
    yaxis_title="Trust Score",
    height=400,
    hovermode='x unified',
    template="plotly_white"
)

st.plotly_chart(fig_trend, use_container_width=True)

# ==================== AGENT SCORES ====================
st.subheader("🤖 Multi-Agent Analysis Scores")

col1, col2, col3 = st.columns(3)

agent_data = {
    "Bias Detection": {"score": 92, "status": "✅", "issues": 0},
    "Privacy Detection": {"score": 84, "status": "⚠️", "issues": 2},
    "Compliance": {"score": 85, "status": "⚠️", "issues": 3},
    "Security": {"score": 88, "status": "✅", "issues": 1},
    "Explainability": {"score": 91, "status": "✅", "issues": 0},
    "Risk Prediction": {"score": 83, "status": "⚠️", "issues": 2}
}

agent_names = list(agent_data.keys())
agent_scores = [agent_data[name]["score"] for name in agent_names]

fig_agents = go.Figure(data=[
    go.Bar(
        y=agent_names,
        x=agent_scores,
        orientation='h',
        marker=dict(
            color=['#2ecc71' if score >= 85 else '#f39c12' if score >= 70 else '#e74c3c' for score in agent_scores],
            line=dict(color='rgba(0,0,0,0.1)', width=1)
        ),
        text=[f"{score}/100" for score in agent_scores],
        textposition='outside'
    )
])

fig_agents.update_layout(
    title="",
    xaxis_title="Score",
    yaxis_title="",
    height=400,
    xaxis=dict(range=[0, 100]),
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(fig_agents, use_container_width=True)

# ==================== COMPLIANCE STATUS ====================
st.subheader("📋 Regulatory Compliance Status")

compliance_data = {
    "Framework": ["EU AI Act", "GDPR Article 22", "SEC AI Rules", "California Law", "Industry-Specific"],
    "Status": ["⚠️ Needs Action", "⚠️ Needs Action", "✅ Compliant", "⚠️ Needs Action", "✅ Compliant"],
    "Progress": [65, 72, 100, 58, 95]
}

df_compliance = pd.DataFrame(compliance_data)

col1, col2 = st.columns([2, 1])

with col1:
    st.dataframe(
        df_compliance,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Progress": st.column_config.ProgressColumn(
                "Progress",
                min_value=0,
                max_value=100,
            )
        }
    )

with col2:
    compliant_count = len([s for s in compliance_data["Status"] if "✅" in s])
    st.info(f"**{compliant_count}/{len(compliance_data['Status'])}** Frameworks Compliant")

# ==================== RISK PREDICTIONS ====================
st.subheader("🔮 30-Day Risk Forecast")

risk_predictions = pd.DataFrame({
    "Risk Type": [
        "Fairness Drift",
        "Data Drift",
        "Accuracy Degradation",
        "Regulatory Action",
        "Security Vulnerability"
    ],
    "Probability": [0.18, 0.35, 0.22, 0.08, 0.05],
    "Recommended Action": [
        "Monitor demographics",
        "Plan retraining",
        "Collect validation data",
        "Maintain documentation",
        "Security hardening"
    ]
})

fig_risks = go.Figure(data=[
    go.Bar(
        x=risk_predictions["Risk Type"],
        y=risk_predictions["Probability"] * 100,
        marker=dict(
            color=['#e74c3c' if p > 0.3 else '#f39c12' if p > 0.1 else '#2ecc71' for p in risk_predictions["Probability"]]
        ),
        text=[f"{p*100:.0f}%" for p in risk_predictions["Probability"]],
        textposition='outside'
    )
])

fig_risks.update_layout(
    title="",
    yaxis_title="Probability (%)",
    xaxis_title="",
    height=350,
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(fig_risks, use_container_width=True)

st.dataframe(
    risk_predictions,
    use_container_width=True,
    hide_index=True
)

# ==================== TOP RECOMMENDATIONS ====================
st.subheader("💡 Top Recommendations (Ranked by Impact)")

recommendations = [
    ("🔴 CRITICAL", "Implement differential privacy mechanisms", "Privacy Risk - Est. Impact: +15 points"),
    ("🟠 HIGH", "Collect diverse training data for underrepresented groups", "Fairness - Est. Impact: +8 points"),
    ("🟠 HIGH", "Add human review threshold for edge cases", "Governance - Est. Impact: +6 points"),
    ("🟡 MEDIUM", "Document feature importance explanations", "Explainability - Est. Impact: +4 points"),
    ("🟡 MEDIUM", "Set up automated data drift monitoring", "Monitoring - Est. Impact: +3 points"),
]

for priority, action, impact in recommendations:
    st.write(f"{priority} **{action}**")
    st.caption(f"→ {impact}")
    st.divider()

# ==================== NEXT ACTIONS ====================
st.subheader("📅 Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        "🔄 **Next Auto Re-certification**\n\n"
        "In 28 days\n\n"
        "Or manually re-run analysis now"
    )

with col2:
    st.warning(
        "⚠️ **Action Required**\n\n"
        "3 high-priority recommendations pending\n\n"
        "Est. time to resolve: 2 weeks"
    )

with col3:
    st.success(
        "✅ **Production Ready**\n\n"
        "Model approved for deployment\n\n"
        "With continuous monitoring enabled"
    )

st.divider()

if st.button("📊 View Detailed Agent Reports"):
    st.switch_page("pages/2_Detailed_Analysis.py")

if st.button("🔄 Run New Analysis"):
    st.switch_page("pages/3_Upload_Model.py")
