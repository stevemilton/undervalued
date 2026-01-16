"""Common Pydantic schemas for pagination, filtering, and errors."""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, per_page: int
    ) -> "PaginatedResponse[T]":
        """Factory method to create paginated response."""
        pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        return cls(items=items, total=total, page=page, per_page=per_page, pages=pages)


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")


class ErrorDetail(BaseModel):
    """Error detail for validation errors."""

    loc: List[str] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str | List[ErrorDetail] = Field(..., description="Error details")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(default="0.1.0", description="API version")
