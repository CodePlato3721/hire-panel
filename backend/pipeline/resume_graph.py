# graph/resume_graph.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from .schemas.jd_schemas import ScoringCriteria
from .nodes.score_resumes import score_resumes


class Resume(TypedDict):
    filename: str
    content: str
    total_score: int
    reason: str
    detail: str


class HRMemory(TypedDict):
    scoring_preferences: list[str]
    adjustment_history: list[str]


class ResumeState(TypedDict):
    messages: Annotated[list, add_messages]
    scoring_criteria: list[ScoringCriteria]
    resumes: list[Resume]
    hr_memory: HRMemory


def build_resume_graph(checkpointer):
    builder = StateGraph(ResumeState)

    builder.add_node("score_resumes", score_resumes)

    builder.add_edge(START, "score_resumes")
    builder.add_edge("score_resumes", END)

    return builder.compile(checkpointer=checkpointer)