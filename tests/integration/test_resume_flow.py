# tests/integration/test_resume_flow.py
from pipeline import build_resume_graph
from .sample_data import SAMPLE_RESUME

resume_graph = build_resume_graph()
resume_config = {"configurable": {"thread_id": "resume"}}


def _stream_and_print(graph, inputs, config):
    for event in graph.stream(inputs, config):
        for value in event.values():
            if value and "messages" in value:
                print(f"\nAssistant: {value['messages'][-1].content}")


def run_resume_flow(criteria: list[dict]) -> list[dict]:
    """Score sample resume. Returns scored resumes."""

    print("\n" + "=" * 60)
    print("STEP 2: Score resume")
    print("=" * 60)

    _stream_and_print(resume_graph, {
        "messages": [],
        "scoring_criteria": criteria,
        "resumes": [{
            "filename": "john_doe.pdf",
            "content": SAMPLE_RESUME,
            "total_score": None,
            "reason": "",
            "detail": "",
        }],
        "hr_memory": {
            "scoring_preferences": [],
            "adjustment_history": [],
        }
    }, resume_config)

    state = resume_graph.get_state(resume_config)
    resumes = state.values["resumes"]
    print(f"\nScore: {resumes[0]['total_score']} pts")
    print(f"Reason: {resumes[0]['reason']}")
    return resumes