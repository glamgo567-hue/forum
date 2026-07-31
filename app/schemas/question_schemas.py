from datetime import datetime

from pydantic import BaseModel


class QuestionCreate(BaseModel):
    title: str 
    body: str

class QuestionRead(BaseModel):
    id: int 
    title: str
    body: str
    views: int
    author_id: int
    created_at: datetime

    model_config={"from_attributes": True}

class QuestionUpdate(BaseModel):
    title: str | None = None
    body: str | None = None