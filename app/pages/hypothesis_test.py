import streamlit as st

st.dataframe(st.session_state.get("data"))