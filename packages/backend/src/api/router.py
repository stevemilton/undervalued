"""Main API router aggregator."""

from fastapi import APIRouter

from .v1 import opportunities_router, properties_router, system_router

api_router = APIRouter(prefix="/api")

# Include v1 routers
api_router.include_router(opportunities_router, prefix="/v1")
api_router.include_router(properties_router, prefix="/v1")
api_router.include_router(system_router, prefix="/v1")


__all__ = ["api_router"]
