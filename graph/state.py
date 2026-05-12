# graph/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class ScoringCriteria(TypedDict):
    name: str
    description: str


class Resume(TypedDict):
    filename: str
    content: str
    total_score: int
    reason: str       # one-line summary
    detail: str       # breakdown per criterion


class HRMemory(TypedDict):
    scoring_preferences: list[str]  # HR preferences learned over time
    adjustment_history: list[str]   # past correction records


class JDState(TypedDict):
    messages: Annotated[list, add_messages]
    job_requirements: str
    scoring_criteria: list[ScoringCriteria]


class ResumeState(TypedDict):
    messages: Annotated[list, add_messages]
    scoring_criteria: list[ScoringCriteria]  # passed in from JD flow
    resumes: list[Resume]
    hr_memory: HRMemory