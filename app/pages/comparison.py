import streamlit as st
import requests

url = "http://localhost:8000/test"
response = requests.get(url)
st.write(response.json()["status"])