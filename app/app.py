import streamlit as st
from utils.streamlit_config import init, survey_selector

# Initialize the application
init()

if st.session_state["init"]:
    # --- SIDEBAR ---
    with st.sidebar:
        survey_selector()