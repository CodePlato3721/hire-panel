import pytest
from unittest.mock import MagicMock, patch
from langgraph.types import Command

from pipeline.nodes.approve_criteria import approve_criteria
from pipeline.utils import format_criteria


# ---------------------------------------------------------------------------
# format_criteria
# ---------------------------------------------------------------------------

def test_format_criteria_multiple():
    criteria = [
        {"name": "Python", "description": "3+ years"},
        {"name": "Communication", "description": "Clear writing"},
    ]
    result = format_criteria(criteria)
    assert result == "- **Python**: 3+ years\n- **Communication**: Clear writing"


def test_format_criteria_single():
    criteria = [{"name": "SQL", "description": "Basic queries"}]
    assert format_criteria(criteria) == "- **SQL**: Basic queries"


def test_format_criteria_empty():
    assert format_criteria([]) == ""


# ---------------------------------------------------------------------------
# approve_criteria — approval path
# ---------------------------------------------------------------------------

SAMPLE_STATE = {
    "messages": [],
    "job_requirements": "Some JD",
    "scoring_criteria": [{"name": "Python", "description": "3+ years"}],
}

APPROVED_KEYWORDS = ["ok", "yes", "confirm", "looks good", "good"]


@pytest.mark.parametrize("keyword", APPROVED_KEYWORDS)
def test_approve_all_keywords(keyword):
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": keyword}):
        result = approve_criteria(SAMPLE_STATE)

    assert isinstance(result, Command)
    assert result.goto == "__end__"
    message_content = result.update["messages"][0].content
    assert "confirmed" in message_content.lower() or "resumes" in message_content.lower()


def test_approve_strips_whitespace():
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": "  ok  "}):
        result = approve_criteria(SAMPLE_STATE)

    assert result.goto == "__end__"


def test_approve_missing_feedback_key_defaults_to_ok():
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={}):
        result = approve_criteria(SAMPLE_STATE)

    assert result.goto == "__end__"


# ---------------------------------------------------------------------------
# approve_criteria — revision path
# ---------------------------------------------------------------------------

def _make_llm_mock(revised_criteria):
    mock_llm = MagicMock()
    mock_result = MagicMock()
    mock_result.criteria = revised_criteria
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_result
    return mock_llm


def test_revision_loops_back():
    revised = [{"name": "Python", "description": "5+ years"}, {"name": "Leadership", "description": "Team lead exp"}]
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": "add leadership criterion"}), \
         patch("pipeline.nodes.approve_criteria.llm", _make_llm_mock(revised)):
        result = approve_criteria(SAMPLE_STATE)

    assert result.goto == "approve_criteria"


def test_revision_updates_scoring_criteria():
    revised = [{"name": "Python", "description": "5+ years"}]
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": "needs more experience"}), \
         patch("pipeline.nodes.approve_criteria.llm", _make_llm_mock(revised)):
        result = approve_criteria(SAMPLE_STATE)

    assert result.update["scoring_criteria"] == revised


# ---------------------------------------------------------------------------
# Boundary conditions
# ---------------------------------------------------------------------------

def test_approve_uppercase_keyword():
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": "OK"}):
        result = approve_criteria(SAMPLE_STATE)

    assert result.goto == "__end__"


def test_empty_feedback_goes_to_revision():
    revised = [{"name": "Python", "description": "3+ years"}]
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": ""}), \
         patch("pipeline.nodes.approve_criteria.llm", _make_llm_mock(revised)):
        result = approve_criteria(SAMPLE_STATE)

    assert result.goto == "approve_criteria"


def test_approve_with_empty_scoring_criteria():
    state = {**SAMPLE_STATE, "scoring_criteria": []}
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": "ok"}):
        result = approve_criteria(state)

    assert result.goto == "__end__"


def test_revision_with_empty_scoring_criteria():
    state = {**SAMPLE_STATE, "scoring_criteria": []}
    revised = [{"name": "Python", "description": "3+ years"}]
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": "add python criterion"}), \
         patch("pipeline.nodes.approve_criteria.llm", _make_llm_mock(revised)):
        result = approve_criteria(state)

    assert result.update["scoring_criteria"] == revised


