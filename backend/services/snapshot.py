from dataclasses import dataclass

from backend.services.db import get_checkpointer
from backend.services.session import graph_config
from pipeline.jd_graph import build_jd_graph
from pipeline.resume_graph import build_resume_graph
from pipeline.feedback_graph import build_feedback_graph

EMPTY_HR_MEMORY: dict = {"scoring_preferences": [], "adjustment_history": []}


def _vals(snap) -> dict:
    return snap.values if snap and snap.values else {}


@dataclass
class SessionSnapshot:
    criteria: list
    resumes_in_feedback: list
    resumes_in_resume: list
    hr_memory: dict
    jd_pending: bool

    @property
    def resumes(self) -> list:
        return self.resumes_in_feedback or self.resumes_in_resume


async def fetch_session_snapshot(session_id: str) -> SessionSnapshot:
    checkpointer = get_checkpointer()

    jd_snap = await build_jd_graph(checkpointer).aget_state(graph_config(session_id, "jd"))
    resume_snap = await build_resume_graph(checkpointer).aget_state(graph_config(session_id, "resume"))
    feedback_snap = await build_feedback_graph(checkpointer).aget_state(graph_config(session_id, "feedback"))

    return SessionSnapshot(
        criteria=_vals(jd_snap).get("scoring_criteria", []),
        resumes_in_feedback=_vals(feedback_snap).get("resumes") or [],
        resumes_in_resume=_vals(resume_snap).get("resumes") or [],
        hr_memory=_vals(feedback_snap).get("hr_memory") or _vals(resume_snap).get("hr_memory") or EMPTY_HR_MEMORY,
        jd_pending=bool(jd_snap and "approve_criteria" in (jd_snap.next or [])),
    )


async def get_criteria(session_id: str) -> list:
    checkpointer = get_checkpointer()
    jd_snap = await build_jd_graph(checkpointer).aget_state(graph_config(session_id, "jd"))
    return _vals(jd_snap).get("scoring_criteria", [])
