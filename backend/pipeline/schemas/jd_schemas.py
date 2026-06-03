# graph/schemas/jd_schemas.py
from typing import TypedDict
from pydantic import BaseModel


class ScoringCriteria(TypedDict):
    name: str
    description: str


class ExtractedCriteria(BaseModel):
    criteria: list[ScoringCriteria]
    summary: str