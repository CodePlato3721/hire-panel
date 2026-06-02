import io
import json
from typing import List

import pdfplumber
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from backend.services.resume import build_resume_stream
from backend.routers.sse import events_to_sse_tokens

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
    events, graph, config = await build_resume_stream(session_id, resumes)
    return StreamingResponse(_stream_resume(events, graph, config), media_type="text/event-stream")
