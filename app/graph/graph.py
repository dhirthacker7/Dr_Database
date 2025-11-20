from typing import Dict, Any, Callable
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.graph.nodes import (
    classify_intent_node,
    metadata_node,
    dq_node,
    sql_node,
    rootcause_node,
    final_node
)

from app.warehouse.client import get_warehouse_client


# --------------------------------------------------------
# Graph state typing
# --------------------------------------------------------
class GraphState(Dict[str, Any]):
    """
    Expected fields:
      question: str
      tables: list[str]
      sql_text: str | None
      intent: str
      answer: str
      debug: list[str]
    """
    pass


# --------------------------------------------------------
# Helper to wrap nodes with DB
# --------------------------------------------------------
def wrap(node_fn: Callable, db: Session):
    def wrapped(state: Dict[str, Any]):
        return node_fn(state, db)
    return wrapped


# --------------------------------------------------------
# Build graph
# --------------------------------------------------------
def build_graph(db: Session):
    graph = StateGraph(GraphState)

    # Nodes
    graph.add_node("classify_intent", wrap(classify_intent_node, db))
    graph.add_node("metadata", wrap(metadata_node, db))
    graph.add_node("dq", wrap(dq_node, db))
    graph.add_node("sql", wrap(sql_node, db))
    graph.add_node("rootcause", wrap(rootcause_node, db))
    graph.add_node("final", wrap(final_node, db))

    # Start → Intent
    graph.set_entry_point("classify_intent")

    # Branching based on intent
    graph.add_conditional_edges(
        "classify_intent",
        lambda state: state.get("intent"),
        {
            "metadata": "metadata",
            "dq": "dq",
            "sql": "sql",
            "rootcause": "rootcause",
        }
    )

    # All agents → final
    graph.add_edge("metadata", "final")
    graph.add_edge("dq", "final")
    graph.add_edge("sql", "final")
    graph.add_edge("rootcause", "final")

    # final → END
    graph.add_edge("final", END)

    return graph.compile()


# --------------------------------------------------------
# Public function used by FastAPI
# --------------------------------------------------------
def run_langgraph_query(question: str, tables, sql_text, db: Session):
    """
    This is called by routes_ui to execute the entire LangGraph pipeline.
    """
    state: GraphState = {
        "question": question,
        "tables": tables or [],
        "sql_text": sql_text,
        "intent": None,
        "answer": None,
        "debug": [],
    }

    app = build_graph(db)
    result = app.invoke(state)
    return result
