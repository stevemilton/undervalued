"""HistoricalTransaction model - Land Registry price paid data."""

import enum
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .property import Property


class TransactionCategory(str, enum.Enum):
    """Transaction category classification from Land Registry."""

    STANDARD = "Standard"
    ADDITIONAL = "Additional"


class HistoricalTransaction(Base, TimestampMixin):
    """
    Historical transaction model from HM Land Registry Price Paid data.

    Stores individual property sales with price, date, and category.
    Used for calculating market benchmarks (PPSF).

    Attributes:
        transaction_id: UUID primary key
        uprn: FK to property
        price_paid: Transaction price in GBP
        date_of_transfer: Sale completion date
        transaction_category: Standard or Additional price
    """

    __tablename__ = "historical_transactions"

    transaction_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    uprn: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("properties.uprn"),
        index=True,
        nullable=False,
        comment="FK to property UPRN",
    )
    price_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Transaction price in GBP",
    )
    date_of_transfer: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Sale completion date",
    )
    transaction_category: Mapped[TransactionCategory] = mapped_column(
        Enum(TransactionCategory),
        nullable=False,
        comment="Standard or Additional price",
    )

    # Relationships
    property: Mapped["Property"] = relationship(
        "Property",
        back_populates="historical_transactions",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<HistoricalTransaction(id={self.transaction_id}, price={self.price_paid})>"
