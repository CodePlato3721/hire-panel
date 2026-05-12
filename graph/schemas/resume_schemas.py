# graph/schemas/resume_schemas.py
from pydantic import BaseModel


class CriterionScore(BaseModel):
    name: str        # criterion name
    score: int       # 1-10
    justification: str  # one sentence explanation


class ResumeScoringResult(BaseModel):
    criterion_scores: list[CriterionScore]
    total_score: int  # sum of all criterion scores
    reason: str       # one-line candidate summary
    detail: str       # full breakdown