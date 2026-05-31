import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from backend.schemas.feedback import FeedbackRequest
from backend.services.db import get_checkpointer
from backend.services.session import graph_config
from backend.routers.sse import events_to_sse_tokens
from pipeline.jd_graph import build_jd_graph
from pipeline.resume_graph import build_resume_graph
from pipeline.feedback_graph import build_feedback_graph

router = APIRouter(prefix="/api/sessions", tags=["feedback"])

_EMPTY_HR_MEMORY = {"scoring_preferences": [], "adjustment_history": []}


async def _stream_feedback(events, graph, config):
    async for token in events_to_sse_tokens(events):
        yield token
    state = await graph.aget_state(config)
    yield f"data: {json.dumps({'type': 'done', 'resumes': state.values.get('resumes', []), 'hr_memory': state.values.get('hr_memory', {})})}\n\n"


@router.post("/{session_id}/feedback")
async def submit_feedback(session_id: str, req: FeedbackRequest):
    checkpointer = get_checkpointer()

    jd_state = await build_jd_graph(checkpointer).aget_state(graph_config(session_id, "jd"))
    criteria = jd_state.values.get("scoring_criteria", [])

    feedback_config = graph_config(session_id, "feedback")
    graph = build_feedback_graph(checkpointer)
    prev = await graph.aget_state(feedback_config)

    if prev and prev.values:
        resumes = prev.values.get("resumes", [])
        hr_memory = prev.values.get("hr_memory", _EMPTY_HR_MEMORY)
    else:
        resume_state = await build_resume_graph(checkpointer).aget_state(graph_config(session_id, "resume"))
        resumes = resume_state.values.get("resumes", [])
        hr_memory = _EMPTY_HR_MEMORY
    events = graph.astream_events(
        {
            "messages": [HumanMessage(content=req.feedback)],
            "scoring_criteria": criteria,
            "resumes": resumes,
            "hr_memory": hr_memory,
        },
        feedback_config,
        version="v2",
    )
    return StreamingResponse(_stream_feedback(events, graph, feedback_config), media_type="text/event-stream")
