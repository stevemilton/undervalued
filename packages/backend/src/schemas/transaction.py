"""Pydantic schemas for HistoricalTransaction model."""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    """Base transaction schema."""

    uprn: str = Field(..., min_length=1, max_length=12, description="Property UPRN")
    price_paid: Decimal = Field(..., gt=0, description="Transaction price in GBP")
    date_of_transfer: date = Field(..., description="Sale completion date")
    transaction_category: str = Field(..., description="Standard or Additional")


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    pass


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""

    transaction_id: UUID

    class Config:
        """Pydantic config."""

        from_attributes = True


class TransactionWithPPSF(TransactionResponse):
    """Transaction with calculated price per square foot."""

    price_per_sqft: Optional[float] = Field(None, description="Calculated PPSF")
    floor_area_sqft: Optional[float] = Field(None, description="Floor area used for calculation")


class ComparableTransaction(BaseModel):
    """Comparable transaction for analysis."""

    uprn: str
    address: Optional[dict] = None
    price_paid: Decimal
    date_of_transfer: date
    floor_area_sqft: Optional[float] = None
    price_per_sqft: Optional[float] = None
    distance_meters: Optional[float] = Field(None, description="Distance from subject property")

    class Config:
        """Pydantic config."""

        from_attributes = True
