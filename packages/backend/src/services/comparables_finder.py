"""Comparables Finder - Finds similar properties for PPSF comparison.

Searches for comparable transactions in the same postcode sector
with similar property characteristics.
"""

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import HistoricalTransaction, Property
from .ppsf_calculator import ComparableProperty

logger = logging.getLogger(__name__)


@dataclass
class ComparableSearchCriteria:
    """Criteria for finding comparable properties."""

    postcode_sector: str  # e.g., "SW15 6"
    property_type: Optional[str] = None
    min_floor_area_sqft: Optional[float] = None
    max_floor_area_sqft: Optional[float] = None
    max_age_months: int = 24
    limit: int = 100


class ComparablesFinder:
    """
    Finds comparable properties for valuation analysis.

    Comparables are selected based on:
    - Same postcode sector (geographic proximity)
    - Similar property type (optional)
    - Similar floor area (optional)
    - Within time window

    Example:
        >>> finder = ComparablesFinder(db_session)
        >>> comparables = await finder.find(
        ...     postcode_sector="SW15 6",
        ...     property_type="Terraced",
        ...     floor_area_sqft=1250
        ... )
    """

    # Floor area tolerance for "similar" properties
    FLOOR_AREA_TOLERANCE = 0.25  # 25%

    def __init__(self, db: AsyncSession):
        """
        Initialize the finder.

        Args:
            db: Async database session
        """
        self.db = db

    async def find(
        self,
        postcode_sector: str,
        property_type: Optional[str] = None,
        floor_area_sqft: Optional[float] = None,
        max_age_months: int = 24,
        limit: int = 100,
    ) -> List[ComparableProperty]:
        """
        Find comparable transactions.

        Args:
            postcode_sector: Postcode sector (e.g., "SW15 6")
            property_type: Filter by property type
            floor_area_sqft: Target floor area for range filtering
            max_age_months: Maximum transaction age
            limit: Maximum results

        Returns:
            List of ComparableProperty objects
        """
        cutoff_date = date.today() - timedelta(days=max_age_months * 30)

        # Build query
        query = (
            select(HistoricalTransaction, Property)
            .join(Property, HistoricalTransaction.uprn == Property.uprn)
            .where(HistoricalTransaction.date_of_transfer >= cutoff_date)
            .where(Property.floor_area_sqft.isnot(None))
            .where(Property.floor_area_sqft > 0)
        )

        # Add postcode filter
        query = query.where(
            Property.address_bs7666["postcode"].astext.startswith(postcode_sector)
        )

        # Add property type filter if specified
        if property_type:
            query = query.where(Property.property_type == property_type)

        # Add floor area range filter if specified
        if floor_area_sqft and floor_area_sqft > 0:
            min_area = floor_area_sqft * (1 - self.FLOOR_AREA_TOLERANCE)
            max_area = floor_area_sqft * (1 + self.FLOOR_AREA_TOLERANCE)
            query = query.where(
                and_(
                    Property.floor_area_sqft >= min_area,
                    Property.floor_area_sqft <= max_area,
                )
            )

        # Order by most recent first
        query = query.order_by(HistoricalTransaction.date_of_transfer.desc())
        query = query.limit(limit)

        # Execute query
        result = await self.db.execute(query)
        rows = result.all()

        # Convert to ComparableProperty objects
        comparables = []
        for transaction, property_obj in rows:
            ppsf = float(transaction.price_paid) / property_obj.floor_area_sqft
            comparables.append(
                ComparableProperty(
                    uprn=transaction.uprn,
                    postcode=property_obj.address_bs7666.get("postcode", ""),
                    property_type=property_obj.property_type.value if hasattr(property_obj.property_type, 'value') else str(property_obj.property_type),
                    price_paid=float(transaction.price_paid),
                    floor_area_sqft=property_obj.floor_area_sqft,
                    transaction_date=transaction.date_of_transfer,
                    ppsf=round(ppsf, 2),
                )
            )

        logger.info(
            f"Found {len(comparables)} comparables in {postcode_sector} "
            f"(type={property_type}, area={floor_area_sqft})"
        )

        return comparables

    async def find_for_property(
        self,
        uprn: str,
        max_age_months: int = 24,
        limit: int = 50,
    ) -> List[ComparableProperty]:
        """
        Find comparables for a specific property.

        Automatically uses the property's postcode, type, and floor area.

        Args:
            uprn: Property UPRN
            max_age_months: Maximum transaction age
            limit: Maximum results

        Returns:
            List of ComparableProperty objects
        """
        # Get property details
        result = await self.db.execute(
            select(Property).where(Property.uprn == uprn)
        )
        property_obj = result.scalar_one_or_none()

        if not property_obj:
            logger.warning(f"Property not found: {uprn}")
            return []

        # Extract postcode sector
        postcode = property_obj.address_bs7666.get("postcode", "")
        postcode_sector = self._extract_sector(postcode)

        if not postcode_sector:
            logger.warning(f"Invalid postcode for property {uprn}: {postcode}")
            return []

        return await self.find(
            postcode_sector=postcode_sector,
            property_type=property_obj.property_type.value if hasattr(property_obj.property_type, 'value') else str(property_obj.property_type),
            floor_area_sqft=property_obj.floor_area_sqft,
            max_age_months=max_age_months,
            limit=limit,
        )

    def _extract_sector(self, postcode: str) -> Optional[str]:
        """Extract postcode sector from full postcode."""
        if not postcode:
            return None

        parts = postcode.strip().upper().split()
        if len(parts) == 2 and len(parts[1]) >= 1:
            return f"{parts[0]} {parts[1][0]}"

        return None
