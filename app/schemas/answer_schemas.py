from datetime import datetime

from pydantic import BaseModel


class AnswerCreate(BaseModel):
    body: str
    question_id: int

class AnswerRead(BaseModel):
    id: int
    body: str
    is_accepted: bool
    created_at: datetime
    author_id: int
    question_id: int

    model_config={"from_attributes": True}

class AnswerUpdate(BaseModel):
    body: str