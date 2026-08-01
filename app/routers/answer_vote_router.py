from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.answer_model import Answer
from app.models.user_model import User
from app.models.vote_model import Vote
from app.schemas.vote_schemas import VoteIn

a_vote_router = APIRouter(prefix="/answers/{answer_id}/vote", tags=["answer_votes"])

@a_vote_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_vote(answer_id: int,
                      vote_data: VoteIn,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.answer_id == answer_id,))).scalar_one_or_none()
    if vote is not None:
        raise HTTPException(status_code=409, detail="Have you already voted")
    new_vote = Vote(value=vote_data.value,
                    user_id=current_user.id,
                    answer_id=answer_id)
    db.add(new_vote)
    await db.commit()
    await db.refresh(new_vote)
    return new_vote

@a_vote_router.patch("/")
async def patch_vote(answer_id: int,
                     vote_data: VoteIn,
                     current_user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.answer_id == answer_id,))).scalar_one_or_none()
    if vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    vote.value = vote_data.value
    await db.commit()
    await db.refresh(vote)
    return vote

@a_vote_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def del_vote(answer_id: int,
                   current_user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.answer_id == answer_id,))).scalar_one_or_none()
    if vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    await db.delete(vote)
    await db.commit()
