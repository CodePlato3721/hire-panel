from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    feedback: str
