"""ActiveListing model - Current property listings from scraped sources."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Date, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .property import Property


class ActiveListing(Base, TimestampMixin):
    """
    Active listing model for properties currently on the market.

    Stores scraped data from property portals (Rightmove, Zoopla).

    Attributes:
        listing_id: UUID primary key
        external_url: Original listing URL (unique)
        asking_price: Current asking price in GBP
        listing_date: Date property was listed
        agent_name: Estate agent name
        source: Portal source (rightmove, zoopla)
        raw_data: Original scraped data as JSONB
    """

    __tablename__ = "active_listings"

    listing_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    external_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        comment="Original listing URL",
    )
    asking_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Asking price in GBP",
    )
    listing_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date property was listed",
    )
    agent_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Estate agent name",
    )
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Portal source (rightmove, zoopla)",
    )
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Original scraped data",
    )

    # Relationships
    property: Mapped[Optional["Property"]] = relationship(
        "Property",
        back_populates="current_listing",
        uselist=False,
        foreign_keys="Property.current_listing_id",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ActiveListing(id={self.listing_id}, price={self.asking_price})>"
