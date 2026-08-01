from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.question_model import Question
from app.models.user_model import User
from app.models.vote_model import Vote
from app.schemas.vote_schemas import VoteIn

q_vote_router = APIRouter(prefix="/questions/{question_id}/vote", tags=["question_votes"])

@q_vote_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_vote(question_id: int,
                      vote_data: VoteIn,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.question_id == question_id,))).scalar_one_or_none()
    if vote is not None:
        raise HTTPException(status_code=409, detail="Have you already voted")
    new_vote = Vote(value=vote_data.value,
                    user_id=current_user.id,
                    question_id=question_id)
    db.add(new_vote)
    await db.commit()
    await db.refresh(new_vote)
    return new_vote

@q_vote_router.patch("/")
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
    vote.value = vote_data.value
    await db.commit()
    await db.refresh(vote)
    return vote

@q_vote_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def del_vote(question_id: int,
                   current_user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    vote = (await db.execute(select(Vote).where(Vote.user_id == current_user.id, Vote.question_id == question_id,))).scalar_one_or_none()
    if vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    await db.delete(vote)
    await db.commit()
