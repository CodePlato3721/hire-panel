import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langgraph.types import Command

from backend.schemas.jd import JDSubmitRequest, JDReplyRequest
from backend.services.db import get_checkpointer
from backend.routers.sse import events_to_sse_tokens
from pipeline.jd_graph import build_jd_graph

router = APIRouter(prefix="/api/sessions", tags=["jd"])


async def _stream_jd(events, graph, config):
    async for token in events_to_sse_tokens(events):
        yield token
    state = await graph.aget_state(config)
    yield f"data: {json.dumps({'type': 'done', 'interrupted': bool(state.next), 'criteria': state.values.get('scoring_criteria', [])})}\n\n"


@router.post("/{session_id}/jd")
async def submit_jd(session_id: str, req: JDSubmitRequest):
    graph = build_jd_graph(get_checkpointer())
    config = {"configurable": {"thread_id": session_id}}
    events = graph.astream_events(
        {"messages": [], "job_requirements": req.jd_text, "scoring_criteria": []},
        config,
        version="v2",
    )
    return StreamingResponse(_stream_jd(events, graph, config), media_type="text/event-stream")


@router.post("/{session_id}/jd/reply")
async def reply_jd(session_id: str, req: JDReplyRequest):
    graph = build_jd_graph(get_checkpointer())
    config = {"configurable": {"thread_id": session_id}}
    events = graph.astream_events(
        Command(resume={"feedback": req.reply}),
        config,
        version="v2",
    )
    return StreamingResponse(_stream_jd(events, graph, config), media_type="text/event-stream")
