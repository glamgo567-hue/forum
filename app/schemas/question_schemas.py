from datetime import datetime

from pydantic import BaseModel

from app.schemas.tag_schemas import TagOut


class QuestionCreate(BaseModel):
    title: str 
    body: str
    tags: list[str] = []

class QuestionRead(BaseModel):
    id: int 
    title: str
    body: str
    views: int
    author_id: int
    created_at: datetime
    tags: list[TagOut] = []
    score: int
    my_vote: int | None = None  
    
    model_config={"from_attributes": True}

class QuestionUpdate(BaseModel):
    title: str | None = None
    body: str | None = None