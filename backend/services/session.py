def graph_config(session_id: str, graph: str) -> dict:
    return {"configurable": {"thread_id": f"{session_id}:{graph}"}}
