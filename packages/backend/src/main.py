"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .config import get_settings
from .schemas import HealthResponse

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    logger.info("Starting Undervalued API", env=settings.app_env)
    yield
    logger.info("Shutting down Undervalued API")


app = FastAPI(
    title="Undervalued API",
    description="UK Property Opportunity Finder - Identify undervalued properties using Land Registry data",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_tags=[
        {"name": "opportunities", "description": "Search for undervalued properties"},
        {"name": "properties", "description": "Property analysis and details"},
        {"name": "system", "description": "System administration and data ingestion"},
    ],
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Undervalued API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
