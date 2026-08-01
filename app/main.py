from fastapi import FastAPI, status

from app.routers.answer_router import answer_router
from app.routers.answer_vote_router import a_vote_router
from app.routers.auth_router import auth_router
from app.routers.question_router import question_router
from app.routers.question_vote_router import q_vote_router

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(question_router)
app.include_router(answer_router)
app.include_router(a_vote_router)
app.include_router(q_vote_router)