from pydantic import BaseModel


class JDSubmitRequest(BaseModel):
    jd_text: str


class JDReplyRequest(BaseModel):
    reply: str
