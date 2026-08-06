from pathlib import Path

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.answer_router import answer_router
from app.routers.answer_vote_router import a_vote_router
from app.routers.auth_router import auth_router
from app.routers.question_router import question_router
from app.routers.question_vote_router import q_vote_router

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

API_PREFIX = "/api"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(question_router, prefix=API_PREFIX)
app.include_router(answer_router, prefix=API_PREFIX)
app.include_router(a_vote_router, prefix=API_PREFIX)
app.include_router(q_vote_router, prefix=API_PREFIX)

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        candidate = (FRONTEND_DIST / full_path).resolve()
        if full_path and candidate.is_file() and candidate.is_relative_to(FRONTEND_DIST):
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")