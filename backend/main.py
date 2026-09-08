"""Bizora AI Business Manager — FastAPI application entrypoint."""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai.routes import router as chat_router
from api.analytics import router as analytics_router
from api.auth import router as auth_router
from api.businesses import router as businesses_router
from api.upload import router as upload_router
from config import settings
from database.connection import Base, engine

logging.basicConfig(level=logging.INFO)


def ensure_database_ready() -> None:
    """Creates tables when the app starts so the owner does not need manual DB setup."""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables checked and initialized successfully")
    except Exception:
        logging.exception("Database initialization failed")
        raise


ensure_database_ready()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI Business Manager for small businesses: CSV import, "
                "cleaning, analytics, forecasting, and an AI manager.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Request-Id"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth_router)
app.include_router(businesses_router)
app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "debug": settings.DEBUG}
