from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vote_model import Vote


async def get_score(db: AsyncSession, *, question_id: int | None = None, answer_id: int | None = None) -> int:
    query = select(func.coalesce(func.sum(Vote.value), 0))
    if question_id is not None:
        query = query.where(Vote.question_id == question_id)
    else:
        query = query.where(Vote.answer_id == answer_id)
    return (await db.execute(query)).scalar()


async def get_my_vote(db: AsyncSession, user_id: int | None, *, question_id: int | None = None, answer_id: int | None = None) -> int | None:
    if user_id is None:
        return None
    query = select(Vote.value).where(Vote.user_id == user_id)
    if question_id is not None:
        query = query.where(Vote.question_id == question_id)
    else:
        query = query.where(Vote.answer_id == answer_id)
    return (await db.execute(query)).scalar_one_or_none()