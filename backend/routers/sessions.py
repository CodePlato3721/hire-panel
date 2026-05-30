import uuid
from fastapi import APIRouter
from backend.schemas.session import SessionCreateResponse, SessionStateResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
async def create_session():
    return SessionCreateResponse(session_id=str(uuid.uuid4()))


@router.get("/{session_id}", response_model=SessionStateResponse)
async def get_session(session_id: str):
    return SessionStateResponse(
        session_id=session_id,
        stage="idle",
        criteria=[],
        resumes=[],
        hr_memory={"scoring_preferences": [], "adjustment_history": []},
    )
