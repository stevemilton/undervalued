"""ValuationMetrics model - Computed property valuation data."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .property import Property


class OpportunityPriority(str, enum.Enum):
    """Opportunity priority classification based on discount percentage."""

    HIGH = "High"  # > 15% discount
    MEDIUM = "Medium"  # > 5% discount
    LOW = "Low"  # Fair value or overpriced


class ValuationMetrics(Base):
    """
    Valuation metrics model with pre-computed analysis data.

    Stores the "Bargain Index" calculation results for quick retrieval.

    Attributes:
        id: UUID primary key
        uprn: FK to property (unique)
        current_ppsf: Asking price per square foot
        market_ppsf_12m: Average sold PPSF in area (12 months)
        undervalued_index: Discount percentage (positive = undervalued)
        projected_yield: Estimated annual rental yield
        comparable_count: Number of comparable transactions used
        priority: Opportunity classification (High/Medium/Low)
        calculated_at: Timestamp of calculation
    """

    __tablename__ = "valuation_metrics"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    uprn: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("properties.uprn"),
        unique=True,
        nullable=False,
        index=True,
        comment="FK to property UPRN",
    )
    current_ppsf: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Asking price per square foot",
    )
    market_ppsf_12m: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Average sold PPSF in area (12 months)",
    )
    undervalued_index: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Discount percentage (positive = undervalued)",
    )
    projected_yield: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Estimated annual rental yield",
    )
    comparable_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of comparable transactions used",
    )
    priority: Mapped[Optional[OpportunityPriority]] = mapped_column(
        Enum(OpportunityPriority),
        nullable=True,
        comment="Opportunity classification",
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp of calculation",
    )

    # Relationships
    property: Mapped["Property"] = relationship(
        "Property",
        back_populates="valuation_metrics",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ValuationMetrics(uprn={self.uprn}, priority={self.priority})>"
