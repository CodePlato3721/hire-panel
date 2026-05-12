# graph/nodes/process_feedback.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.types import Command
from ..state import ResumeState
from ..schemas.feedback_schemas import FeedbackAnalysis
from ..prompts.feedback_prompts import PROCESS_FEEDBACK_SYSTEM

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _analyze_feedback(feedback: str, state: ResumeState) -> FeedbackAnalysis:
    """Use LLM to extract preferences and adjustments from HR feedback."""
    criteria_text = "\n".join(
        f"- {c['name']}: {c['description']}"
        for c in state["scoring_criteria"]
    )
    resumes_summary = "\n".join(
        f"- {r['filename']}: {r['total_score']} pts — {r['reason']}"
        for r in state["resumes"]
    )
    return llm.with_structured_output(FeedbackAnalysis).invoke([
        {"role": "system", "content": PROCESS_FEEDBACK_SYSTEM},
        {"role": "user", "content": (
            f"Current criteria:\n{criteria_text}\n\n"
            f"Current resume scores:\n{resumes_summary}\n\n"
            f"HR feedback:\n{feedback}"
        )}
    ])


def process_feedback(state: ResumeState) -> Command:
    """Process HR feedback, update memory, and route to rescore if needed."""
    # Get the latest HR message
    feedback = state["messages"][-1].content

    analysis = _analyze_feedback(feedback, state)

    # Update HR memory
    updated_memory = {
        "scoring_preferences": (
            state["hr_memory"]["scoring_preferences"] + analysis.new_preferences
        ),
        "adjustment_history": (
            state["hr_memory"]["adjustment_history"] + analysis.adjustments
        ),
    }

    update = {
        "hr_memory": updated_memory,
        "messages": [AIMessage(content=(
            f"Understood. I've noted your feedback:\n\n"
            + (
                "**New preferences learned:**\n" +
                "\n".join(f"- {p}" for p in analysis.new_preferences) + "\n\n"
                if analysis.new_preferences else ""
            )
            + (
                "**Adjustments to apply:**\n" +
                "\n".join(f"- {a}" for a in analysis.adjustments)
                if analysis.adjustments else ""
            )
            + "\n\nRe-scoring all resumes now..."
        ))]
    }

    # Update criteria if HR changed weights
    if analysis.has_criteria_change:
        update["scoring_criteria"] = [
            {"name": c.name, "description": c.description}
            for c in analysis.updated_criteria
        ]

    return Command(update=update, goto="rescore_all")