# graph/schemas/jd_schemas.py
from pydantic import BaseModel
from ..state import ScoringCriteria


class ExtractedCriteria(BaseModel):
    criteria: list[ScoringCriteria]
    summary: str