"""Property model - UPRN-anchored property records."""

import enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .listing import ActiveListing
    from .metrics import ValuationMetrics
    from .transaction import HistoricalTransaction


class PropertyType(str, enum.Enum):
    """Property type classification."""

    DETACHED = "Detached"
    SEMI_DETACHED = "Semi-Detached"
    TERRACED = "Terraced"
    FLAT = "Flat"


class Property(Base, TimestampMixin):
    """
    Property model representing a unique UK property.

    Uses UPRN (Unique Property Reference Number) as the natural primary key
    for seamless integration with Land Registry data.

    Attributes:
        uprn: 12-digit Unique Property Reference Number
        address_bs7666: BS7666-compliant address as JSONB
        floor_area_sqft: Floor area in square feet (from EPC)
        property_type: Classification (Detached, Semi-Detached, etc.)
        epc_rating: Energy Performance Certificate rating (A-G)
        current_listing_id: FK to active listing if property is on market
    """

    __tablename__ = "properties"

    uprn: Mapped[str] = mapped_column(
        String(12),
        primary_key=True,
        index=True,
        comment="Unique Property Reference Number",
    )
    address_bs7666: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="BS7666 address: {paon, saon, street, town, postcode}",
    )
    floor_area_sqft: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Floor area in square feet from EPC",
    )
    property_type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType),
        nullable=False,
        comment="Property classification",
    )
    epc_rating: Mapped[Optional[str]] = mapped_column(
        String(1),
        nullable=True,
        comment="EPC rating A-G",
    )
    current_listing_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("active_listings.listing_id"),
        nullable=True,
        comment="FK to current active listing",
    )

    # Relationships
    historical_transactions: Mapped[list["HistoricalTransaction"]] = relationship(
        "HistoricalTransaction",
        back_populates="property",
        cascade="all, delete-orphan",
    )
    current_listing: Mapped[Optional["ActiveListing"]] = relationship(
        "ActiveListing",
        back_populates="property",
        foreign_keys=[current_listing_id],
    )
    valuation_metrics: Mapped[Optional["ValuationMetrics"]] = relationship(
        "ValuationMetrics",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Property(uprn={self.uprn}, type={self.property_type.value})>"
