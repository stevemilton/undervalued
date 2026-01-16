"""Pydantic schemas for ActiveListing model."""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ListingBase(BaseModel):
    """Base listing schema."""

    external_url: str = Field(..., max_length=500, description="Original listing URL")
    asking_price: Decimal = Field(..., gt=0, description="Asking price in GBP")
    listing_date: date = Field(..., description="Date listed")
    agent_name: Optional[str] = Field(None, max_length=200, description="Estate agent name")
    source: str = Field(..., max_length=50, description="Source portal (rightmove, zoopla)")


class ListingCreate(ListingBase):
    """Schema for creating a listing."""

    raw_data: Optional[dict] = Field(None, description="Original scraped data")


class ListingUpdate(BaseModel):
    """Schema for updating a listing (partial)."""

    asking_price: Optional[Decimal] = Field(None, gt=0)
    agent_name: Optional[str] = Field(None, max_length=200)


class ListingResponse(ListingBase):
    """Schema for listing response."""

    listing_id: UUID

    class Config:
        """Pydantic config."""

        from_attributes = True


class ListingInOpportunity(BaseModel):
    """Simplified listing for opportunity views."""

    listing_id: UUID
    external_url: str
    asking_price: Decimal
    listing_date: date
    agent_name: Optional[str] = None
    source: str

    class Config:
        """Pydantic config."""

        from_attributes = True
