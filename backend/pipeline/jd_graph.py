# graph/jd_graph.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from .schemas.jd_schemas import ScoringCriteria
from .nodes.extract_jd import extract_jd
from .nodes.approve_criteria import approve_criteria


class JDState(TypedDict):
    messages: Annotated[list, add_messages]
    job_requirements: str
    scoring_criteria: list[ScoringCriteria]


def build_jd_graph(checkpointer):
    builder = StateGraph(JDState)

    builder.add_node("extract_jd", extract_jd)
    builder.add_node("approve_criteria", approve_criteria)

    builder.add_edge(START, "extract_jd")
    builder.add_edge("extract_jd", "approve_criteria")

    return builder.compile(checkpointer=checkpointer)