import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from backend.pipeline import build_feedback_graph


@pytest.mark.e2e
def test_jd_extracts_criteria(criteria):
    assert 4 <= len(criteria) <= 6, f"Expected 4-6 criteria, got {len(criteria)}"
    for c in criteria:
        assert c.get("name"), "Each criterion must have a name"


@pytest.mark.e2e
def test_resume_scoring(scored_resumes):
    assert len(scored_resumes) == 1
    resume = scored_resumes[0]
    assert resume["total_score"] is not None, "total_score should be set after scoring"
    assert resume["reason"], "reason should be non-empty after scoring"


@pytest.mark.e2e
def test_feedback_rescoring(criteria, scored_resumes):
    graph = build_feedback_graph(InMemorySaver())
    config = {"configurable": {"thread_id": "e2e-feedback"}}
    feedback = "The LangChain experience should be weighted more heavily."
    for _ in graph.stream(
        {
            "messages": [HumanMessage(content=feedback)],
            "scoring_criteria": criteria,
            "resumes": scored_resumes,
            "hr_memory": {"scoring_preferences": [], "adjustment_history": []},
        },
        config,
    ):
        pass
    state = graph.get_state(config)
    final_resumes = state.values["resumes"]
    hr_memory = state.values["hr_memory"]
    assert final_resumes[0]["total_score"] is not None
    assert len(hr_memory["scoring_preferences"]) > 0, "hr_memory should capture feedback preferences"
