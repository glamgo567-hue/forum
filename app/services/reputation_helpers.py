from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User


def get_reputation_delta(value: int, target_type: Literal["question", "answer"]) -> int:
    if value == 1:
        return 10 if target_type == "answer" else 5
    return -5

async def apply_reputation_change(db: AsyncSession, user_id: int, delta: int) -> None:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        return
    user.reputation = user.reputation + delta