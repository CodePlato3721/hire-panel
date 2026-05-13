import pytest
from unittest.mock import MagicMock, patch
from langgraph.types import Command

from pipeline.nodes.approve_criteria import approve_criteria, _format_criteria


# ---------------------------------------------------------------------------
# _format_criteria
# ---------------------------------------------------------------------------

def test_format_criteria_multiple():
    criteria = [
        {"name": "Python", "description": "3+ years"},
        {"name": "Communication", "description": "Clear writing"},
    ]
    result = _format_criteria(criteria)
    assert result == "- **Python**: 3+ years\n- **Communication**: Clear writing"


def test_format_criteria_single():
    criteria = [{"name": "SQL", "description": "Basic queries"}]
    assert _format_criteria(criteria) == "- **SQL**: Basic queries"


def test_format_criteria_empty():
    assert _format_criteria([]) == ""


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


def test_revision_message_contains_revised_criteria():
    revised = [{"name": "Go", "description": "2+ years"}]
    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": "switch to Go"}), \
         patch("pipeline.nodes.approve_criteria.llm", _make_llm_mock(revised)):
        result = approve_criteria(SAMPLE_STATE)

    content = result.update["messages"][0].content
    assert "Go" in content
    assert "2+ years" in content


def test_revision_llm_receives_current_criteria_and_feedback():
    revised = [{"name": "Python", "description": "5+ years"}]
    mock_llm = _make_llm_mock(revised)
    feedback_text = "require more seniority"

    with patch("pipeline.nodes.approve_criteria.interrupt", return_value={"feedback": feedback_text}), \
         patch("pipeline.nodes.approve_criteria.llm", mock_llm):
        approve_criteria(SAMPLE_STATE)

    invoke_args = mock_llm.with_structured_output.return_value.invoke.call_args[0][0]
    user_message = invoke_args[1]["content"]
    assert "Python" in user_message
    assert feedback_text in user_message
