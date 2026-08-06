from datetime import datetime

from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    body: str = Field(min_length=1)

class AnswerRead(BaseModel):
    id: int
    body: str
    is_accepted: bool
    created_at: datetime
    author_id: int
    author_username: str
    question_id: int
    score: int
    my_vote: int | None = None  

    model_config={"from_attributes": True}

class AnswerUpdate(BaseModel):
    body: str | None = Field(default=None, min_length=1)