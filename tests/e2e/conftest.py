import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from backend.pipeline import build_jd_graph, build_resume_graph
from tests.e2e.sample_data import SAMPLE_JD, SAMPLE_RESUME


@pytest.fixture(scope="module")
def criteria():
    graph = build_jd_graph(InMemorySaver())
    config = {"configurable": {"thread_id": "e2e-jd"}}
    for _ in graph.stream(
        {"messages": [], "job_requirements": SAMPLE_JD, "scoring_criteria": []}, config
    ):
        pass
    for _ in graph.stream(Command(resume={"feedback": "ok"}), config):
        pass
    return graph.get_state(config).values["scoring_criteria"]


@pytest.fixture(scope="module")
def scored_resumes(criteria):
    graph = build_resume_graph(InMemorySaver())
    config = {"configurable": {"thread_id": "e2e-resume"}}
    for _ in graph.stream(
        {
            "messages": [],
            "scoring_criteria": criteria,
            "resumes": [
                {
                    "filename": "john_doe.pdf",
                    "content": SAMPLE_RESUME,
                    "total_score": None,
                    "reason": "",
                    "detail": "",
                }
            ],
            "hr_memory": {"scoring_preferences": [], "adjustment_history": []},
        },
        config,
    ):
        pass
    return graph.get_state(config).values["resumes"]
