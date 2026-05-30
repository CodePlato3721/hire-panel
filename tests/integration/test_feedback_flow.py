# tests/integration/test_feedback_flow.py
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from pipeline import build_feedback_graph

feedback_graph = build_feedback_graph(InMemorySaver())
feedback_config = {"configurable": {"thread_id": "feedback"}}


def _stream_and_print(graph, inputs, config):
    for event in graph.stream(inputs, config):
        for value in event.values():
            if value and "messages" in value:
                print(f"\nAssistant: {value['messages'][-1].content}")


def run_feedback_flow(criteria: list[dict], resumes: list[dict]):
    """Process HR feedback and rescore all resumes."""

    print("\n" + "=" * 60)
    print("STEP 3: HR feedback and rescore")
    print("=" * 60)

    feedback = "The LangChain experience should be weighted more heavily."
    print(f"\n[HR]: {feedback}")

    _stream_and_print(feedback_graph, {
        "messages": [HumanMessage(content=feedback)],
        "scoring_criteria": criteria,
        "resumes": resumes,
        "hr_memory": {
            "scoring_preferences": [],
            "adjustment_history": [],
        }
    }, feedback_config)

    state = feedback_graph.get_state(feedback_config)
    final_resumes = state.values["resumes"]
    print(f"\nRevised score: {final_resumes[0]['total_score']} pts")
    print(f"Reason: {final_resumes[0]['reason']}")