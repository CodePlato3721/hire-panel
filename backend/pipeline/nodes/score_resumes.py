# graph/nodes/score_resumes.py
from __future__ import annotations
from typing import TYPE_CHECKING
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from ..schemas.resume_schemas import ResumeScoringResult
if TYPE_CHECKING:
    from ..resume_graph import ResumeState
from ..prompts.resume_prompts import SCORE_RESUME_SYSTEM

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _build_scoring_context(state: ResumeState) -> str:
    """Build criteria and memory context for the scoring prompt."""
    criteria_text = "\n".join(
        f"- {c['name']}: {c['description']}"
        for c in state["scoring_criteria"]
    )
    preferences = "\n".join(state["hr_memory"]["scoring_preferences"]) or "None recorded yet."
    adjustments = "\n".join(state["hr_memory"]["adjustment_history"]) or "None recorded yet."

    return (
        f"Scoring criteria:\n{criteria_text}\n\n"
        f"HR preferences:\n{preferences}\n\n"
        f"Past adjustments:\n{adjustments}"
    )


def _score_single_resume(state: ResumeState, resume: dict) -> dict:
    """Score a single resume and return updated resume dict."""
    result = llm.with_structured_output(ResumeScoringResult).invoke([
        {"role": "system", "content": SCORE_RESUME_SYSTEM},
        {"role": "user", "content": (
            f"{_build_scoring_context(state)}\n\n"
            f"Resume ({resume['filename']}):\n{resume['content']}"
        )}
    ])
    return {
        **resume,
        "total_score": result.total_score,
        "reason": result.reason,
        "detail": result.detail,
    }


def score_resumes(state: ResumeState) -> dict:
    """Score all unscored resumes sequentially."""
    updated_resumes = []
    score_messages = []

    for resume in state["resumes"]:
        # Skip already scored resumes
        if resume.get("total_score") is not None:
            updated_resumes.append(resume)
            continue

        scored = _score_single_resume(state, resume)
        updated_resumes.append(scored)
        score_messages.append(
            f"- **{scored['filename']}**: {scored['total_score']} pts — {scored['reason']}"
        )

    return {
        "resumes": updated_resumes,
        "messages": [AIMessage(content=(
            f"Scored {len(score_messages)} resume(s):\n\n" +
            "\n".join(score_messages)
        ))]
    }