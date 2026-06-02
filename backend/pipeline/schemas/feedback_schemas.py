# graph/schemas/feedback_schemas.py
from pydantic import BaseModel


class UpdatedCriterion(BaseModel):
    name: str
    description: str


class FeedbackAnalysis(BaseModel):
    new_preferences: list[str]             # new rules to add to HR memory
    adjustments: list[str]                 # specific resume score changes requested
    updated_criteria: list[UpdatedCriterion]  # updated scoring criteria if HR changed weights
    has_criteria_change: bool              # whether criteria need to be updated