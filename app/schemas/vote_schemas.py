from typing import Literal

from pydantic import BaseModel


class VoteIn(BaseModel):
    value: Literal[1, -1]

class VoteRead(BaseModel):
    id: int
    value: int
    user_id: int
    question_id: int | None 
    answer_id: int | None

    model_config = {"from_attributes": True}