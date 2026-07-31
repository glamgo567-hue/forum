from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.answer_model import Answer
from app.models.question_model import Question
from app.models.user_model import User
from app.schemas.answer_schemas import AnswerCreate, AnswerRead, AnswerUpdate

answer_router = APIRouter()

@answer_router.post("/questions/{question_id}/answers", response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
async def create_answer(answer_data: AnswerCreate,
                        question_id: int,
                        current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    new_answer = Answer(body=answer_data.body,
                        question_id=question_id,
                        author_id=current_user.id)
    db.add(new_answer)
    await db.commit()
    await db.refresh(new_answer)
    return new_answer

@answer_router.get("/questions/{question_id}/answers", response_model=list[AnswerRead])
async def show_answers(question_id: int,
                       skip: int = 0, 
                       limit: int = 10,
                       db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    answer = (await db.execute(select(Answer).where(Answer.question_id==question_id).offset(skip).limit(limit))).scalars().all()
    return answer

@answer_router.patch("/answers/{answer_id}", response_model=AnswerRead)
async def patch_answer(answer_id: int,
                       answer_data: AnswerUpdate,
                       current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    if answer.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_answer_data = answer_data.model_dump(exclude_unset=True)
    for key, value in update_answer_data.items():
        setattr(answer, key, value)
    await db.commit()
    await db.refresh(answer)
    return answer

@answer_router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_answer(answer_id: int,
                     current_user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    if answer.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await db.delete(answer)
    await db.commit()