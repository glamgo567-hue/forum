from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.answer_model import Answer
from app.models.user_model import User
from app.models.vote_model import Vote
from app.schemas.vote_schemas import VoteIn, VoteRead
from app.services.reputation_helpers import (
    apply_reputation_change,
    get_reputation_delta,
)

a_vote_router = APIRouter(prefix="/answers/{answer_id}", tags=["answer_votes"])

@a_vote_router.post("/vote",response_model=VoteRead, status_code=status.HTTP_201_CREATED)
async def create_vote(answer_id: int,
                      vote_data: VoteIn,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
            raise HTTPException(status_code=404, detail="Answer not found")
    if answer.author_id == current_user.id:
        raise HTTPException(status_code=403, detail="You cannot vote on your own answer")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.answer_id == answer_id,))).scalar_one_or_none()
    if vote is not None:
        raise HTTPException(status_code=409, detail="You have already voted")
    new_vote = Vote(value=vote_data.value,
                    user_id=current_user.id,
                    answer_id=answer_id)
    delta = get_reputation_delta(vote_data.value, "answer")
    await apply_reputation_change(db, answer.author_id, delta)
    db.add(new_vote)
    await db.commit()
    await db.refresh(new_vote)
    return new_vote

@a_vote_router.patch("/vote", response_model=VoteRead)
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
    old_value = vote.value
    vote.value = vote_data.value
    old_delta = get_reputation_delta(old_value, "answer")
    new_delta = get_reputation_delta(vote_data.value, "answer")
    await apply_reputation_change(db, answer.author_id, new_delta - old_delta)
    await db.commit()
    await db.refresh(vote)
    return vote

@a_vote_router.delete("/vote", status_code=status.HTTP_204_NO_CONTENT)
async def del_vote(answer_id: int,
                   current_user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.answer_id == answer_id,))).scalar_one_or_none()
    if vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    delta = get_reputation_delta(vote.value, "answer")
    await apply_reputation_change(db, answer.author_id, -delta)
    await db.delete(vote)
    await db.commit()
