from app.agents.base import get_llm


def run_sql_agent(user_query: str, sql_text: str | None = None) -> str:
    """
    Explains or helps with SQL questions.
    """
    llm = get_llm()

    prompt = f"""
You are Dr. Database's SQL Expert Agent.

User question:
{user_query}

SQL snippet (may be empty):
{sql_text or "(none provided)"}

If SQL is provided, explain what it does, suggest improvements,
and adapt to SQL Server if relevant.
If no SQL is provided, answer the question about SQL best you can.
"""

    resp = llm.invoke(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)
