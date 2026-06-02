import uuid
from fastapi import APIRouter
from backend.schemas.session import SessionCreateResponse, SessionStateResponse
from backend.services.snapshot import fetch_session_snapshot

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
async def create_session():
    return SessionCreateResponse(session_id=str(uuid.uuid4()))


@router.get("/{session_id}", response_model=SessionStateResponse)
async def get_session(session_id: str):
    snap = await fetch_session_snapshot(session_id)

    if snap.resumes_in_feedback:
        stage = "feedback_done"
    elif snap.resumes_in_resume:
        stage = "resume_done"
    elif snap.jd_pending:
        stage = "jd_pending"
    elif snap.criteria:
        stage = "jd_done"
    else:
        stage = "idle"

    return SessionStateResponse(
        session_id=session_id,
        stage=stage,
        criteria=snap.criteria,
        resumes=snap.resumes,
        hr_memory=snap.hr_memory,
    )
