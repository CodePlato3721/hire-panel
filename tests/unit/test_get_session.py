import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.routers.sessions import get_session


def _snap(values=None, next_nodes=None):
    s = MagicMock()
    s.values = values or {}
    s.next = next_nodes or []
    return s


def _run(jd_snap, resume_snap, feedback_snap):
    with (
        patch("backend.services.snapshot.get_checkpointer"),
        patch("backend.services.snapshot.build_jd_graph") as mock_jd,
        patch("backend.services.snapshot.build_resume_graph") as mock_res,
        patch("backend.services.snapshot.build_feedback_graph") as mock_fb,
    ):
        mock_jd.return_value.aget_state = AsyncMock(return_value=jd_snap)
        mock_res.return_value.aget_state = AsyncMock(return_value=resume_snap)
        mock_fb.return_value.aget_state = AsyncMock(return_value=feedback_snap)
        return asyncio.run(get_session("sess-1"))


def test_stage_idle():
    result = _run(_snap(), _snap(), _snap())
    assert result.stage == "idle"
    assert result.criteria == []
    assert result.resumes == []
    assert result.hr_memory == {"scoring_preferences": [], "adjustment_history": []}


def test_stage_jd_pending():
    jd = _snap(
        values={"scoring_criteria": [{"name": "Python", "description": "..."}]},
        next_nodes=["approve_criteria"],
    )
    result = _run(jd, _snap(), _snap())
    assert result.stage == "jd_pending"
    assert result.criteria == [{"name": "Python", "description": "..."}]


def test_stage_jd_done():
    jd = _snap(values={"scoring_criteria": [{"name": "Python", "description": "..."}]})
    result = _run(jd, _snap(), _snap())
    assert result.stage == "jd_done"
    assert result.criteria == [{"name": "Python", "description": "..."}]


def test_stage_resume_done():
    jd = _snap(values={"scoring_criteria": [{"name": "Python", "description": "..."}]})
    res = _snap(values={
        "resumes": [{"filename": "a.pdf", "total_score": 30, "reason": "ok", "detail": ""}],
        "hr_memory": {"scoring_preferences": [], "adjustment_history": []},
    })
    result = _run(jd, res, _snap())
    assert result.stage == "resume_done"
    assert len(result.resumes) == 1
    assert result.resumes[0]["total_score"] == 30


def test_stage_feedback_done():
    jd = _snap(values={"scoring_criteria": [{"name": "Python", "description": "..."}]})
    res = _snap(values={
        "resumes": [{"filename": "a.pdf", "total_score": 30, "reason": "ok", "detail": ""}],
        "hr_memory": {"scoring_preferences": [], "adjustment_history": []},
    })
    fb = _snap(values={
        "resumes": [{"filename": "a.pdf", "total_score": 35, "reason": "updated", "detail": ""}],
        "hr_memory": {"scoring_preferences": ["prefer LangChain exp"], "adjustment_history": []},
    })
    result = _run(jd, res, fb)
    assert result.stage == "feedback_done"
    assert result.resumes[0]["total_score"] == 35
    assert result.hr_memory["scoring_preferences"] == ["prefer LangChain exp"]
