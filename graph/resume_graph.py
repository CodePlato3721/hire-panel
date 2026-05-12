# graph/resume_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import ResumeState
from .nodes.score_resumes import score_resumes


def build_resume_graph():
    builder = StateGraph(ResumeState)

    builder.add_node("score_resumes", score_resumes)

    builder.add_edge(START, "score_resumes")
    builder.add_edge("score_resumes", END)

    return builder.compile(checkpointer=InMemorySaver())