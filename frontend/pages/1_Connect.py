import streamlit as st
from utils.api import save_connection, test_connection

st.title("🔌 Connect to Warehouse")

# Status check
connected, conn_error = test_connection()

if connected:
    st.success("✅ Backend has an active database connection.")
else:
    st.warning("⚠ No active database connection detected.")

with st.form("db_form"):
    st.subheader("Connection Details")

    col1, col2 = st.columns(2)

    db_type = st.selectbox(
        "Database Type",
        ["mssql", "postgres"],
        format_func=lambda x: "SQL Server (MSSQL)" if x == "mssql" else "Postgres",
    )

    with col1:
        host = st.text_input("Host / Server", "DHIR")
        database = st.text_input("Database Name")

    with col2:
        port = st.text_input("Port", "1433")
        username = st.text_input("Username")

    password = st.text_input("Password", type="password")

    submitted = st.form_submit_button("Save & Test Connection")

if submitted:
    payload = {
        "db_type": db_type,
        "host": host,
        "port": port,
        "database": database,
        "username": username,
        "password": password,
    }

    with st.spinner("Validating connection..."):
        ok, err = save_connection(payload)

    if ok:
        st.success(f"🎉 Connected to database: {database}")
        st.session_state["connected"] = True
    else:
        st.session_state["connected"] = False
        st.error(f"❌ Connection failed: {err}")
