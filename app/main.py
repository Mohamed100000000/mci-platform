"""
نقطة الدخول الرئيسية لتطبيق AZDA Marine Competency Index (MCI) Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="منصة إدارة تدريب وكفاءة بحرية شاملة لمعهد AZDA للتدريب البحري",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["عام"])
def root():
    return {
        "message": "AZDA Marine Competency Index (MCI) Platform API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["عام"])
def health_check():
    return {"status": "ok"}
