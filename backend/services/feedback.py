from langchain_core.messages import HumanMessage

from backend.services.db import get_checkpointer
from backend.services.session import graph_config
from backend.services.snapshot import get_criteria, EMPTY_HR_MEMORY
from pipeline.resume_graph import build_resume_graph
from pipeline.feedback_graph import build_feedback_graph


async def _get_prev_feedback(session_id: str, checkpointer, graph, feedback_config):
    prev = await graph.aget_state(feedback_config)
    if prev and prev.values:
        return prev.values.get("resumes", []), prev.values.get("hr_memory", EMPTY_HR_MEMORY)
    resume_snap = await build_resume_graph(checkpointer).aget_state(graph_config(session_id, "resume"))
    return (resume_snap.values or {}).get("resumes", []), EMPTY_HR_MEMORY


async def build_feedback_stream(session_id: str, feedback_text: str):
    checkpointer = get_checkpointer()
    criteria = await get_criteria(session_id)

    feedback_config = graph_config(session_id, "feedback")
    graph = build_feedback_graph(checkpointer)
    resumes, hr_memory = await _get_prev_feedback(session_id, checkpointer, graph, feedback_config)

    events = graph.astream_events(
        {
            "messages": [HumanMessage(content=feedback_text)],
            "scoring_criteria": criteria,
            "resumes": resumes,
            "hr_memory": hr_memory,
        },
        feedback_config,
        version="v2",
    )
    return events, graph, feedback_config
