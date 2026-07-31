from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.question_model import Question
from app.models.user_model import User
from app.schemas.question_schemas import QuestionCreate, QuestionRead, QuestionUpdate

question_router = APIRouter(prefix="/questions", tags=["/questions"])

@question_router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(quest_data: QuestionCreate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    new_question = Question(title=quest_data.title,
                            body=quest_data.body,
                            author_id=current_user.id,)
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)
    return new_question

@question_router.get("/", response_model=list[QuestionRead])
async def show_questions(skip: int = 0, 
                         limit: int = 10,
                         db: AsyncSession = Depends(get_db)):
    questions = (await db.execute(select(Question).offset(skip).limit(limit))).scalars().all()
    return questions

@question_router.get("/{question_id}", response_model=QuestionRead)
async def show_question(question_id: int, 
                        db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@question_router.patch("/{question_id}", response_model=QuestionRead)
async def patch_question(question_id: int,
                         quest_data: QuestionUpdate,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_quest_data = quest_data.model_dump(exclude_unset=True)
    for key, value in update_quest_data.items():
        setattr(question, key, value)
    await db.commit()
    await db.refresh(question)
    return question

@question_router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_question(question_id: int,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await db.delete(question)
    await db.commit()