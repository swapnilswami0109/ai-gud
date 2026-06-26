import streamlit as st
from PIL import Image
import os

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Guardian OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom CSS
# -----------------------------
css_file = "assets/styles.css"

if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.title("🛡️ AI Guardian OS")

    st.caption("Responsible AI Platform")

    st.divider()

    st.success("System Status: Online")

    st.metric(
        "Compliance",
        "94%"
    )

    st.metric(
        "Models",
        "12"
    )

    st.metric(
        "Projects",
        "8"
    )

    st.divider()

    st.info(
        """
Navigation is available from the
left sidebar using Streamlit Pages.
        """
    )

# -----------------------------
# Header
# -----------------------------
col1, col2 = st.columns([4,1])

with col1:

    st.title("🛡️ AI Guardian OS")

    st.write(
        """
Enterprise Responsible AI Governance Platform

Analyze • Explain • Monitor • Govern
        """
    )

with col2:

    st.metric(
        "Risk Score",
        "LOW"
    )

st.divider()

# -----------------------------
# KPI Cards
# -----------------------------
c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Compliance",
    "94%",
    "+3%"
)

c2.metric(
    "Fairness",
    "91%",
    "+2%"
)

c3.metric(
    "Privacy",
    "93%",
    "+1%"
)

c4.metric(
    "Explainability",
    "95%",
    "+5%"
)

st.divider()

# -----------------------------
# Welcome Section
# -----------------------------
st.header("Welcome")

st.write(
"""
AI Guardian OS helps organizations build
Responsible AI systems by providing

- Dataset Validation
- Bias Detection
- Privacy Scanning
- Explainability
- Compliance Reports
- AI Governance
- Live Monitoring
"""
)

st.info(
"""
Select a page from the sidebar
to begin your Responsible AI workflow.
"""
)