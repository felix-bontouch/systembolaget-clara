import streamlit as st


st.title("Hypotestestning")
st.dataframe(st.session_state.get("data"))