"""API dependency injection providers."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Usage:
        @router.get("/items")
        async def get_items(db: Annotated[AsyncSession, Depends(get_db)]):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_pagination(
    page: int = 1,
    per_page: int = 20,
) -> dict[str, int]:
    """
    Dependency for pagination parameters.

    Usage:
        @router.get("/items")
        async def get_items(pagination: Annotated[dict, Depends(get_pagination)]):
            page = pagination["page"]
            per_page = pagination["per_page"]
    """
    return {"page": max(1, page), "per_page": min(max(1, per_page), 100)}


# Type alias for pagination dependency
Pagination = Annotated[dict[str, int], Depends(get_pagination)]
