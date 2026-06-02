import io
import json
from typing import List

import pdfplumber
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from backend.services.db import get_checkpointer
from backend.services.session import graph_config
from backend.services.snapshot import get_criteria
from backend.routers.sse import events_to_sse_tokens
from pipeline.resume_graph import build_resume_graph

router = APIRouter(prefix="/api/sessions", tags=["resume"])


def _parse_file(data: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    return data.decode("utf-8", errors="replace")


async def _stream_resume(events, graph, config):
    async for token in events_to_sse_tokens(events):
        yield token
    state = await graph.aget_state(config)
    yield f"data: {json.dumps({'type': 'done', 'resumes': state.values.get('resumes', [])})}\n\n"


@router.post("/{session_id}/resumes")
async def upload_resumes(session_id: str, files: List[UploadFile] = File(...)):
    checkpointer = get_checkpointer()

    criteria = await get_criteria(session_id)

    resumes = []
    for f in files:
        data = await f.read()
        resumes.append({
            "filename": f.filename,
            "content": _parse_file(data, f.filename),
            "total_score": None,
            "reason": "",
            "detail": "",
        })

    graph = build_resume_graph(checkpointer)
    config = graph_config(session_id, "resume")
    events = graph.astream_events(
        {
            "messages": [],
            "scoring_criteria": criteria,
            "resumes": resumes,
            "hr_memory": {"scoring_preferences": [], "adjustment_history": []},
        },
        config,
        version="v2",
    )
    return StreamingResponse(_stream_resume(events, graph, config), media_type="text/event-stream")
