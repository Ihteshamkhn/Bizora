"""Bizora AI Business Manager — FastAPI application entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai.routes import router as chat_router
from api.analytics import router as analytics_router
from api.auth import router as auth_router
from api.businesses import router as businesses_router
from api.upload import router as upload_router
from config import settings
from database.connection import Base, engine

logging.basicConfig(level=logging.INFO)

# Create tables on startup (use Alembic migrations in production).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI Business Manager for small businesses: CSV import, "
                "cleaning, analytics, forecasting, and an AI manager.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(businesses_router)
app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
