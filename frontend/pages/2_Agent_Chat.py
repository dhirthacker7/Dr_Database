# frontend/pages/2_Agent_Chat.py
import streamlit as st

from utils.api import fetch_tables, run_agents, test_connection

st.title("💬 Dr. Database — Agent Chat")

# Check connection status
connected, conn_err = test_connection()
if not connected:
    st.error("No active database connection detected. Go to **1_Connect** first to configure the warehouse.")
    st.stop()

st.success("✅ Connected. Chat agent is active.")

st.divider()

# Fetch table list (if any)
tables, tables_err = fetch_tables()
if tables_err:
    st.warning(f"Could not fetch tables: {tables_err}")

question = st.text_area(
    "Ask Dr. Database",
    placeholder="e.g. 'Which tables store customer orders?' or 'Write a CTE to find recent load failures.'",
    height=120,
)

selected_tables = st.multiselect(
    "Optional: select tables to give the agents more context",
    options=tables,
)

sql_input = st.text_area(
    "Optional: provide SQL to explain/analyse",
    placeholder="Paste a SQL query here if you want Dr. Database to explain or debug it.",
    height=150,
)

if st.button("Ask Dr. Database"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Thinking with LangGraph agents..."):
            result, err = run_agents(
                question=question.strip(),
                tables=selected_tables,
                sql_text=sql_input.strip() or None,
            )

        if err:
            st.error(f"❌ Error calling backend: {err}")
        elif not result:
            st.error("No response from backend.")
        else:
            # Main answer
            answer = result.get("answer") or result.get("sql") or "(no answer field)"
            st.subheader("🧠 Answer")
            st.write(answer)

            # Debug trace from LangGraph
            debug = result.get("debug")
            if debug:
                with st.expander("🛠 Debug Trace (LangGraph nodes visited)"):
                    st.write(debug)
