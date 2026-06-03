# graph/nodes/approve_criteria.py
from __future__ import annotations
from typing import TYPE_CHECKING
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.types import Command, interrupt
from ..schemas.jd_schemas import ExtractedCriteria
if TYPE_CHECKING:
    from ..jd_graph import JDState
from ..prompts.jd_prompts import REVISE_CRITERIA_SYSTEM
from ..utils import format_criteria

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

APPROVED_KEYWORDS = {"ok", "yes", "confirm", "looks good", "good"}


def approve_criteria(state: JDState) -> Command:
    """Interrupt and wait for HR approval. Loops until confirmed."""
    human_response = interrupt({"action": "approve_criteria", "criteria": state["scoring_criteria"]})
    feedback = human_response.get("feedback", "ok").strip().lower()

    if feedback in APPROVED_KEYWORDS:
        return Command(
            update={"messages": [AIMessage(content="Criteria confirmed. You can now upload resumes.")]},
            goto="__end__"
        )

    result = llm.with_structured_output(ExtractedCriteria).invoke([
        {"role": "system", "content": REVISE_CRITERIA_SYSTEM},
        {"role": "user", "content": f"Current criteria:\n{state['scoring_criteria']}\n\nHR feedback: {feedback}"}
    ])
    return Command(
        update={
            "scoring_criteria": result.criteria,
            "messages": [AIMessage(content=(
                f"Revised criteria:\n\n{format_criteria(result.criteria)}\n\n"
                f"Reply **ok** to confirm or continue adjusting."
            ))]
        },
        goto="approve_criteria"
    )