import streamlit as st
import pandas as pd

from database.database import get_connection
from utils.auth_guard import require_role

require_role(["Admin"])

st.set_page_config(

    page_title="Admin Dashboard",

    page_icon="🛠️",

    layout="wide"

)

st.title("🛠️ Admin Dashboard")

st.caption(

    "Platform administration and system overview."

)

conn = get_connection()

cursor = conn.cursor()

# Users
cursor.execute(

    "SELECT COUNT(*) FROM users"

)

users = cursor.fetchone()[0]

# Projects
cursor.execute(

    "SELECT COUNT(*) FROM projects"

)

projects = cursor.fetchone()[0]

# Models
cursor.execute(

    "SELECT COUNT(*) FROM models"

)

models = cursor.fetchone()[0]

# Reports
cursor.execute(

    "SELECT COUNT(*) FROM reports"

)

reports = cursor.fetchone()[0]

# Certificates
cursor.execute(

    "SELECT COUNT(*) FROM certificates"

)

certificates = cursor.fetchone()[0]

# Risks
cursor.execute(

    "SELECT COUNT(*) FROM risk_register"

)

risks = cursor.fetchone()[0]

conn.close()

c1,c2,c3 = st.columns(3)

c1.metric(

    "Users",

    users

)

c2.metric(

    "Projects",

    projects

)

c3.metric(

    "Models",

    models

)

c4,c5,c6 = st.columns(3)

c4.metric(

    "Reports",

    reports

)

c5.metric(

    "Certificates",

    certificates

)

c6.metric(

    "Risks",

    risks
)