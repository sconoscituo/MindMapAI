from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import users, mindmaps, payments
from app.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=config.APP_NAME,
    description="AI 마인드맵 자동 생성 + 협업 도구",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(mindmaps.router)
app.include_router(payments.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": config.APP_NAME}
