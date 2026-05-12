# graph/nodes/rescore_all.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from ..state import ResumeState
from ..schemas.resume_schemas import ResumeScoringResult
from ..prompts.resume_prompts import RESCORE_SYSTEM

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _build_rescore_context(state: ResumeState) -> str:
    """Build updated criteria and full adjustment history for rescoring."""
    criteria_text = "\n".join(
        f"- {c['name']}: {c['description']}"
        for c in state["scoring_criteria"]
    )
    preferences = "\n".join(state["hr_memory"]["scoring_preferences"]) or "None recorded yet."
    adjustments = "\n".join(state["hr_memory"]["adjustment_history"]) or "None recorded yet."

    return (
        f"Updated scoring criteria:\n{criteria_text}\n\n"
        f"HR preferences:\n{preferences}\n\n"
        f"Adjustment history:\n{adjustments}"
    )


def rescore_all(state: ResumeState) -> dict:
    """Re-score all resumes using updated criteria and HR memory."""
    context = _build_rescore_context(state)
    updated_resumes = []
    score_messages = []

    for resume in state["resumes"]:
        result = llm.with_structured_output(ResumeScoringResult).invoke([
            {"role": "system", "content": RESCORE_SYSTEM},
            {"role": "user", "content": (
                f"{context}\n\n"
                f"Resume ({resume['filename']}):\n{resume['content']}"
            )}
        ])
        updated = {
            **resume,
            "total_score": result.total_score,
            "reason": result.reason,
            "detail": result.detail,
        }
        updated_resumes.append(updated)
        score_messages.append(
            f"- **{updated['filename']}**: {updated['total_score']} pts — {updated['reason']}"
        )

    return {
        "resumes": updated_resumes,
        "messages": [AIMessage(content=(
            f"All resumes re-scored with updated criteria:\n\n" +
            "\n".join(score_messages)
        ))]
    }