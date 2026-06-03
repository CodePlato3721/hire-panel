# graph/feedback_graph.py
from langgraph.graph import StateGraph, START, END
from .resume_graph import ResumeState
from .nodes.process_feedback import process_feedback
from .nodes.rescore_all import rescore_all


def build_feedback_graph(checkpointer):
    builder = StateGraph(ResumeState)

    builder.add_node("process_feedback", process_feedback)
    builder.add_node("rescore_all", rescore_all)

    builder.add_edge(START, "process_feedback")
    builder.add_edge("rescore_all", END)

    return builder.compile(checkpointer=checkpointer)