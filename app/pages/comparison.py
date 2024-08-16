import streamlit as st
import requests


if "history" not in st.session_state:
     url = "http://localhost:8000/test"
     response = requests.get(url)
     st.session_state["history"] = response.json()

st.title("Jämförelse")
st.write(st.session_state["history"]["status"])