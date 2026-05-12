# tests/integration/test_jd_flow.py
from langgraph.types import Command
from pipeline import build_jd_graph
from .sample_data import SAMPLE_JD

jd_graph = build_jd_graph()
jd_config = {"configurable": {"thread_id": "jd"}}


def _stream_and_print(graph, inputs, config):
    for event in graph.stream(inputs, config):
        for value in event.values():
            if value and "messages" in value:
                print(f"\nAssistant: {value['messages'][-1].content}")


def run_jd_flow() -> list[dict]:
    """Run JD extraction and approval. Returns approved criteria."""

    print("=" * 60)
    print("STEP 1: Extract JD criteria")
    print("=" * 60)

    _stream_and_print(jd_graph, {
        "messages": [],
        "job_requirements": SAMPLE_JD,
        "scoring_criteria": [],
    }, jd_config)

    print("\n[HR]: ok")
    _stream_and_print(jd_graph, Command(resume={"feedback": "ok"}), jd_config)

    state = jd_graph.get_state(jd_config)
    criteria = state.values["scoring_criteria"]
    print(f"\nApproved {len(criteria)} criteria")
    return criteria