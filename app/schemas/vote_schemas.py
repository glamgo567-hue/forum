from typing import Literal

from pydantic import BaseModel


class VoteIn(BaseModel):
    value: Literal[1, -1]