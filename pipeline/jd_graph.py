# graph/jd_graph.py
from langgraph.graph import StateGraph, START
from .state import JDState
from .nodes.extract_jd import extract_jd
from .nodes.approve_criteria import approve_criteria


def build_jd_graph(checkpointer):
    builder = StateGraph(JDState)

    builder.add_node("extract_jd", extract_jd)
    builder.add_node("approve_criteria", approve_criteria)

    builder.add_edge(START, "extract_jd")
    builder.add_edge("extract_jd", "approve_criteria")

    return builder.compile(checkpointer=checkpointer)