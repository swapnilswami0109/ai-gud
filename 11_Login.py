import streamlit as st

from database.auth import login

from database.logger import log

# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------

st.set_page_config(

    page_title="Login",

    page_icon="🔐",

    layout="centered"

)

st.title("🔐 AI Guardian OS Login")

st.caption(

    "Secure access to the Responsible AI Platform"

)

st.divider()

# -----------------------------------------------------
# Session Defaults
# -----------------------------------------------------

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False

if "user" not in st.session_state:

    st.session_state.user = None

if "role" not in st.session_state:

    st.session_state.role = None

# -----------------------------------------------------
# Login Form
# -----------------------------------------------------

email = st.text_input(

    "Email"

)

password = st.text_input(

    "Password",

    type="password"

)

login_btn = st.button(

    "Login",

    type="primary"

)

if login_btn:

    user = login(

        email,

        password

    )

    if user:

        st.session_state.authenticated = True

        st.session_state.user = user["full_name"]

        st.session_state.role = user["role"]

        log(

            user["full_name"],

            "User Login",

            "INFO"

        )

        st.success(

            f"Welcome {user['full_name']}"

        )

        st.rerun()

    else:

        st.error(

            "Invalid email or password."

        )