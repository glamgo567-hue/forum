from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.tag_schemas import TagOut


class QuestionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1)
    tags: list[str] = []

class QuestionRead(BaseModel):
    id: int 
    title: str
    body: str
    author_id: int
    author_username: str
    created_at: datetime
    answer_count: int = 0
    tags: list[TagOut] = []
    score: int
    my_vote: int | None = None  
    
    model_config={"from_attributes": True}

class QuestionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    body: str | None = Field(default=None, min_length=1)