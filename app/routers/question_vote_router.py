from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.question_model import Question
from app.models.user_model import User
from app.models.vote_model import Vote
from app.schemas.vote_schemas import VoteIn, VoteRead
from app.services.reputation_helpers import (
    apply_reputation_change,
    get_reputation_delta,
)

q_vote_router = APIRouter(prefix="/questions/{question_id}", tags=["question_votes"])

@q_vote_router.post("/vote", response_model=VoteRead, status_code=status.HTTP_201_CREATED)
async def create_vote(question_id: int,
                      vote_data: VoteIn,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.author_id == current_user.id:
        raise HTTPException(status_code=403, detail="You cannot vote on your own question")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.question_id == question_id,))).scalar_one_or_none()
    if vote is not None:
        raise HTTPException(status_code=409, detail="You have already voted")
    new_vote = Vote(value=vote_data.value,
                    user_id=current_user.id,
                    question_id=question_id)
    delta = get_reputation_delta(vote_data.value, "question")
    await apply_reputation_change(db, question.author_id, delta)
    db.add(new_vote)
    await db.commit()
    await db.refresh(new_vote)
    return new_vote

@q_vote_router.patch("/vote", response_model=VoteRead)
async def patch_vote(question_id: int,
                     vote_data: VoteIn,
                     current_user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.question_id == question_id,))).scalar_one_or_none()
    if vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    old_value = vote.value
    vote.value = vote_data.value
    old_delta = get_reputation_delta(old_value, "question")
    new_delta = get_reputation_delta(vote_data.value, "question")
    await apply_reputation_change(db, question.author_id, new_delta - old_delta)
    await db.commit()
    await db.refresh(vote)
    return vote

@q_vote_router.delete("/vote", status_code=status.HTTP_204_NO_CONTENT)
async def del_vote(question_id: int,
                   current_user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.question_id == question_id,))).scalar_one_or_none()
    if vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    delta = get_reputation_delta(vote.value, "question")
    await apply_reputation_change(db, question.author_id, -delta)
    await db.delete(vote)
    await db.commit()
