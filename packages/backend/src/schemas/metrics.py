"""Pydantic schemas for ValuationMetrics and Opportunities."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .listing import ListingInOpportunity
from .property import AddressBS7666


class MetricsBase(BaseModel):
    """Base valuation metrics schema."""

    current_ppsf: float = Field(..., description="Asking price per square foot")
    market_ppsf_12m: Optional[float] = Field(None, description="12-month market average PPSF")
    undervalued_index: Optional[float] = Field(None, description="Discount percentage")
    projected_yield: Optional[float] = Field(None, description="Estimated rental yield")
    comparable_count: int = Field(..., ge=0, description="Number of comparables used")
    priority: Optional[str] = Field(None, description="High, Medium, or Low")


class MetricsResponse(MetricsBase):
    """Schema for metrics response."""

    id: UUID
    uprn: str
    calculated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MetricsInOpportunity(BaseModel):
    """Simplified metrics for opportunity list."""

    current_ppsf: float
    market_ppsf_12m: Optional[float] = None
    undervalued_index: Optional[float] = None
    projected_yield: Optional[float] = None
    comparable_count: int
    priority: Optional[str] = None
    calculated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class OpportunityItem(BaseModel):
    """Single opportunity in list view."""

    uprn: str
    address: AddressBS7666
    property_type: str
    floor_area_sqft: Optional[float] = None
    epc_rating: Optional[str] = None
    listing: ListingInOpportunity
    metrics: MetricsInOpportunity

    class Config:
        """Pydantic config."""

        from_attributes = True


class OpportunityFilters(BaseModel):
    """Query filters for opportunities endpoint."""

    postcode_district: str = Field(
        ...,
        min_length=2,
        max_length=4,
        pattern=r"^[A-Z]{1,2}[0-9]{1,2}[A-Z]?$",
        description="Postcode district (e.g., SW15, W14)",
    )
    min_discount_pct: Optional[float] = Field(
        None, ge=0, le=1, description="Minimum discount (0.1 = 10%)"
    )
    max_price: Optional[float] = Field(None, gt=0, description="Maximum asking price")
    property_types: Optional[List[str]] = Field(None, description="Filter by property types")
    sort_by: str = Field(
        default="undervalued_index_desc",
        description="Sort field and direction",
    )


class ChartDataPoint(BaseModel):
    """Data point for price history chart."""

    x: str = Field(..., description="Date string")
    y: float = Field(..., description="PPSF value")
    label: str = Field(..., description="Property label")
    is_subject: bool = Field(default=False, description="Whether this is the subject property")
