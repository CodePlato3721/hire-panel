import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage

from backend.pipeline.nodes.extract_jd import extract_jd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_llm_mock(criteria):
    mock_llm = MagicMock()
    mock_result = MagicMock()
    mock_result.criteria = criteria
    mock_llm.with_structured_output.return_value.invoke.return_value = mock_result
    return mock_llm


SAMPLE_STATE = {
    "messages": [],
    "job_requirements": "We need a senior Python engineer with 5+ years experience.",
    "scoring_criteria": [],
}

SAMPLE_CRITERIA = [
    {"name": "Python", "description": "5+ years"},
    {"name": "Communication", "description": "Clear writing"},
]


# ---------------------------------------------------------------------------
# Return shape
# ---------------------------------------------------------------------------

def test_returns_scoring_criteria():
    with patch("backend.pipeline.nodes.extract_jd.llm", _make_llm_mock(SAMPLE_CRITERIA)):
        result = extract_jd(SAMPLE_STATE)

    assert result["scoring_criteria"] == SAMPLE_CRITERIA


# ---------------------------------------------------------------------------
# Message content
# ---------------------------------------------------------------------------


def test_message_with_empty_criteria():
    with patch("backend.pipeline.nodes.extract_jd.llm", _make_llm_mock([])):
        result = extract_jd(SAMPLE_STATE)

    assert result["scoring_criteria"] == []
    assert isinstance(result["messages"][0], AIMessage)


# ---------------------------------------------------------------------------
# LLM invocation
# ---------------------------------------------------------------------------

def test_llm_called_with_job_requirements():
    mock_llm = _make_llm_mock(SAMPLE_CRITERIA)
    with patch("backend.pipeline.nodes.extract_jd.llm", mock_llm):
        extract_jd(SAMPLE_STATE)

    invoke_args = mock_llm.with_structured_output.return_value.invoke.call_args[0][0]
    user_message = invoke_args[1]["content"]
    assert SAMPLE_STATE["job_requirements"] in user_message



# ---------------------------------------------------------------------------
# Boundary conditions
# ---------------------------------------------------------------------------

def test_empty_job_requirements_passes_empty_string_to_llm():
    state = {**SAMPLE_STATE, "job_requirements": ""}
    mock_llm = _make_llm_mock(SAMPLE_CRITERIA)
    with patch("backend.pipeline.nodes.extract_jd.llm", mock_llm):
        extract_jd(state)

    invoke_args = mock_llm.with_structured_output.return_value.invoke.call_args[0][0]
    user_message = invoke_args[1]["content"]
    assert user_message == "Job description:\n\n"


def test_none_job_requirements_does_not_crash():
    # f-string renders None as the literal string "None" — no TypeError
    state = {**SAMPLE_STATE, "job_requirements": None}
    with patch("backend.pipeline.nodes.extract_jd.llm", _make_llm_mock(SAMPLE_CRITERIA)):
        result = extract_jd(state)

    assert result["scoring_criteria"] == SAMPLE_CRITERIA
    assert isinstance(result["messages"][0], AIMessage)


def test_llm_exception_propagates():
    # extract_jd has no error handling, so LLM errors must surface to the caller
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.side_effect = RuntimeError("API error")
    with patch("backend.pipeline.nodes.extract_jd.llm", mock_llm):
        with pytest.raises(RuntimeError, match="API error"):
            extract_jd(SAMPLE_STATE)
