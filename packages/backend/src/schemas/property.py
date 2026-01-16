"""Pydantic schemas for Property model."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AddressBS7666(BaseModel):
    """BS7666-compliant address structure."""

    paon: Optional[str] = Field(None, description="Primary Addressable Object Name")
    saon: Optional[str] = Field(None, description="Secondary Addressable Object Name")
    street: str = Field(..., description="Street name")
    town: str = Field(..., description="Town or city")
    postcode: str = Field(..., description="UK postcode")


class PropertyBase(BaseModel):
    """Base property schema with common fields."""

    uprn: str = Field(..., min_length=1, max_length=12, description="Unique Property Reference Number")
    address_bs7666: AddressBS7666 = Field(..., description="BS7666 address")
    floor_area_sqft: Optional[float] = Field(None, gt=0, description="Floor area in square feet")
    property_type: str = Field(..., description="Property type (Detached, Semi-Detached, Terraced, Flat)")
    epc_rating: Optional[str] = Field(None, pattern=r"^[A-G]$", description="EPC rating A-G")


class PropertyCreate(PropertyBase):
    """Schema for creating a property."""

    pass


class PropertyUpdate(BaseModel):
    """Schema for updating a property (partial)."""

    floor_area_sqft: Optional[float] = Field(None, gt=0)
    epc_rating: Optional[str] = Field(None, pattern=r"^[A-G]$")
    current_listing_id: Optional[UUID] = None


class PropertyResponse(PropertyBase):
    """Schema for property response."""

    current_listing_id: Optional[UUID] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class PropertyInList(BaseModel):
    """Simplified property for list views."""

    uprn: str
    address: AddressBS7666
    property_type: str
    floor_area_sqft: Optional[float] = None
    epc_rating: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True
