from langgraph.types import Command

from backend.services.db import get_checkpointer
from backend.services.session import graph_config
from backend.pipeline.jd_graph import build_jd_graph


async def build_jd_stream(session_id: str, jd_text: str):
    graph = build_jd_graph(get_checkpointer())
    config = graph_config(session_id, "jd")
    events = graph.astream_events(
        {"messages": [], "job_requirements": jd_text, "scoring_criteria": []},
        config,
        version="v2",
    )
    return events, graph, config


async def build_jd_reply_stream(session_id: str, reply: str):
    graph = build_jd_graph(get_checkpointer())
    config = graph_config(session_id, "jd")
    events = graph.astream_events(
        Command(resume={"feedback": reply}),
        config,
        version="v2",
    )
    return events, graph, config
