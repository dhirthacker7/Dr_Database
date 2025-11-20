# frontend/app.py
import streamlit as st

st.set_page_config(
    page_title="Dr. Database",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Dr. Database")
st.write(
    """
Welcome to **Dr. Database**.

Use the sidebar to:
- Connect to your warehouse
- Chat with the multi-agent system (metadata, SQL, DQ, RCA)
"""
)

st.info("➡ Go to **1_Connect** in the sidebar to set up your database connection.")
