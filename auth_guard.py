import streamlit as st


def require_login():
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in.")
        st.stop()


def require_role(allowed_roles):
    require_login()
    if st.session_state.get("role") not in allowed_roles:
        st.error("Access denied.")
        st.stop()
