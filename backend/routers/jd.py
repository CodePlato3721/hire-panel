import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.schemas.jd import JDSubmitRequest, JDReplyRequest
from backend.services.jd import build_jd_stream, build_jd_reply_stream
from backend.routers.sse import events_to_sse_tokens

router = APIRouter(prefix="/api/sessions", tags=["jd"])


async def _stream_jd(events, graph, config):
    async for token in events_to_sse_tokens(events):
        yield token
    state = await graph.aget_state(config)
    yield f"data: {json.dumps({'type': 'done', 'interrupted': bool(state.next), 'criteria': state.values.get('scoring_criteria', [])})}\n\n"


@router.post("/{session_id}/jd")
async def submit_jd(session_id: str, req: JDSubmitRequest):
    events, graph, config = await build_jd_stream(session_id, req.jd_text)
    return StreamingResponse(_stream_jd(events, graph, config), media_type="text/event-stream")


@router.post("/{session_id}/jd/reply")
async def reply_jd(session_id: str, req: JDReplyRequest):
    events, graph, config = await build_jd_reply_stream(session_id, req.reply)
    return StreamingResponse(_stream_jd(events, graph, config), media_type="text/event-stream")
