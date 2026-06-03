# graph/nodes/extract_jd.py
from __future__ import annotations
from typing import TYPE_CHECKING
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from ..schemas.jd_schemas import ExtractedCriteria
if TYPE_CHECKING:
    from ..jd_graph import JDState
from ..prompts.jd_prompts import EXTRACT_JD_SYSTEM
from ..utils import format_criteria

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def extract_jd(state: JDState) -> dict:
    """Extract scoring criteria from the raw job description text."""
    result = llm.with_structured_output(ExtractedCriteria).invoke([
        {"role": "system", "content": EXTRACT_JD_SYSTEM},
        {"role": "user", "content": f"Job description:\n\n{state['job_requirements']}"}
    ])
    return {
        "scoring_criteria": result.criteria,
        "messages": [AIMessage(content=(
            f"I've extracted the following scoring criteria:\n\n"
            f"{format_criteria(result.criteria)}\n\n"
            f"Reply **ok** to confirm, or tell me what to adjust."
        ))]
    }