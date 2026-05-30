from typing import Any
from pydantic import BaseModel


class SessionCreateResponse(BaseModel):
    session_id: str


class SessionStateResponse(BaseModel):
    session_id: str
    stage: str
    criteria: list[dict[str, Any]]
    resumes: list[dict[str, Any]]
    hr_memory: dict[str, Any]
