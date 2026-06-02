import uuid
from fastapi import APIRouter
from backend.schemas.session import SessionCreateResponse, SessionStateResponse
from backend.services.db import get_checkpointer
from backend.services.session import graph_config
from pipeline.jd_graph import build_jd_graph
from pipeline.resume_graph import build_resume_graph
from pipeline.feedback_graph import build_feedback_graph

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

_EMPTY_HR_MEMORY = {"scoring_preferences": [], "adjustment_history": []}


@router.post("", response_model=SessionCreateResponse)
async def create_session():
    return SessionCreateResponse(session_id=str(uuid.uuid4()))


@router.get("/{session_id}", response_model=SessionStateResponse)
async def get_session(session_id: str):
    checkpointer = get_checkpointer()

    jd_snap = await build_jd_graph(checkpointer).aget_state(graph_config(session_id, "jd"))
    resume_snap = await build_resume_graph(checkpointer).aget_state(graph_config(session_id, "resume"))
    feedback_snap = await build_feedback_graph(checkpointer).aget_state(graph_config(session_id, "feedback"))

    jd_vals = jd_snap.values if jd_snap and jd_snap.values else {}
    resume_vals = resume_snap.values if resume_snap and resume_snap.values else {}
    feedback_vals = feedback_snap.values if feedback_snap and feedback_snap.values else {}

    criteria = jd_vals.get("scoring_criteria", [])
    resumes = feedback_vals.get("resumes") or resume_vals.get("resumes", [])
    hr_memory = (
        feedback_vals.get("hr_memory")
        or resume_vals.get("hr_memory")
        or _EMPTY_HR_MEMORY
    )

    if feedback_vals.get("resumes"):
        stage = "feedback_done"
    elif resume_vals.get("resumes"):
        stage = "resume_done"
    elif jd_snap and "approve_criteria" in (jd_snap.next or []):
        stage = "jd_pending"
    elif criteria:
        stage = "jd_done"
    else:
        stage = "idle"

    return SessionStateResponse(
        session_id=session_id,
        stage=stage,
        criteria=criteria,
        resumes=resumes,
        hr_memory=hr_memory,
    )
