import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.schemas.feedback import FeedbackRequest
from backend.services.feedback import build_feedback_stream
from backend.routers.sse import events_to_sse_tokens

router = APIRouter(prefix="/api/sessions", tags=["feedback"])


async def _stream_feedback(events, graph, config):
    async for token in events_to_sse_tokens(events):
        yield token
    state = await graph.aget_state(config)
    yield f"data: {json.dumps({'type': 'done', 'resumes': state.values.get('resumes', []), 'hr_memory': state.values.get('hr_memory', {})})}\n\n"


@router.post("/{session_id}/feedback")
async def submit_feedback(session_id: str, req: FeedbackRequest):
    events, graph, config = await build_feedback_stream(session_id, req.feedback)
    return StreamingResponse(_stream_feedback(events, graph, config), media_type="text/event-stream")
