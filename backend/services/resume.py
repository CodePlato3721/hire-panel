from backend.services.db import get_checkpointer
from backend.services.session import graph_config
from backend.services.snapshot import get_criteria, EMPTY_HR_MEMORY
from backend.pipeline.resume_graph import build_resume_graph


async def build_resume_stream(session_id: str, resumes: list):
    checkpointer = get_checkpointer()
    criteria = await get_criteria(session_id)
    graph = build_resume_graph(checkpointer)
    config = graph_config(session_id, "resume")
    events = graph.astream_events(
        {
            "messages": [],
            "scoring_criteria": criteria,
            "resumes": resumes,
            "hr_memory": EMPTY_HR_MEMORY,
        },
        config,
        version="v2",
    )
    return events, graph, config
