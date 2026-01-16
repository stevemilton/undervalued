"""API v1 package - aggregates all v1 routers."""

from .opportunities import router as opportunities_router
from .properties import router as properties_router
from .system import router as system_router

__all__ = ["opportunities_router", "properties_router", "system_router"]
