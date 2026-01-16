"""Analysis Service - Orchestrates property valuation analysis.

This is the main entry point for running property analysis, combining
PPSF calculation, comparable search, and bargain scoring.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ActiveListing, Property, ValuationMetrics
from ..models.metrics import OpportunityPriority as DBPriority
from .bargain_calculator import BargainIndexCalculator, BargainScore
from .comparables_finder import ComparablesFinder
from .ppsf_calculator import ComparableProperty, PPSFCalculator, PPSFData

logger = logging.getLogger(__name__)


@dataclass
class PropertyAnalysis:
    """Complete analysis result for a property."""

    uprn: str
    ppsf_data: PPSFData
    bargain_score: BargainScore
    comparables: List[ComparableProperty]
    calculated_at: datetime


class AnalysisService:
    """
    Orchestrates complete property valuation analysis.

    Workflow:
    1. Find comparable transactions in the postcode sector
    2. Calculate PPSF metrics using comparables
    3. Compute bargain score and priority
    4. Optionally persist results to ValuationMetrics

    Example:
        >>> service = AnalysisService(db_session)
        >>> analysis = await service.analyze_property("10024672815")
        >>> print(f"Undervalued: {analysis.bargain_score.undervalued_index:.1%}")
    """

    def __init__(
        self,
        db: AsyncSession,
        ppsf_calculator: Optional[PPSFCalculator] = None,
        bargain_calculator: Optional[BargainIndexCalculator] = None,
    ):
        """
        Initialize the analysis service.

        Args:
            db: Async database session
            ppsf_calculator: Optional custom PPSF calculator
            bargain_calculator: Optional custom bargain calculator
        """
        self.db = db
        self.ppsf_calc = ppsf_calculator or PPSFCalculator()
        self.bargain_calc = bargain_calculator or BargainIndexCalculator()
        self.comparables_finder = ComparablesFinder(db)

    async def analyze_property(
        self,
        uprn: str,
        persist: bool = True,
    ) -> Optional[PropertyAnalysis]:
        """
        Run full analysis for a property.

        Args:
            uprn: Property UPRN
            persist: Whether to save results to database

        Returns:
            PropertyAnalysis with all metrics, or None if property not found
        """
        # Fetch property with current listing
        result = await self.db.execute(
            select(Property)
            .where(Property.uprn == uprn)
            .options()
        )
        property_obj = result.scalar_one_or_none()

        if not property_obj:
            logger.warning(f"Property not found for analysis: {uprn}")
            return None

        # Get current listing for asking price
        listing = None
        if property_obj.current_listing_id:
            listing_result = await self.db.execute(
                select(ActiveListing)
                .where(ActiveListing.listing_id == property_obj.current_listing_id)
            )
            listing = listing_result.scalar_one_or_none()

        if not listing:
            logger.debug(f"No active listing for property {uprn}")
            return None

        if not property_obj.floor_area_sqft or property_obj.floor_area_sqft <= 0:
            logger.debug(f"No floor area for property {uprn}")
            return None

        # Find comparables
        comparables = await self.comparables_finder.find_for_property(
            uprn=uprn,
            max_age_months=24,
            limit=50,
        )

        # Calculate PPSF
        ppsf_data = self.ppsf_calc.calculate(
            asking_price=float(listing.asking_price),
            floor_area_sqft=property_obj.floor_area_sqft,
            comparables=comparables,
        )

        # Calculate bargain score
        bargain_score = self.bargain_calc.calculate(
            ppsf_discount=ppsf_data.discount_pct,
            comparable_count=ppsf_data.comparable_count,
            epc_rating=property_obj.epc_rating,
            property_type=property_obj.property_type.value if hasattr(property_obj.property_type, 'value') else str(property_obj.property_type),
            asking_price=float(listing.asking_price),
        )

        analysis = PropertyAnalysis(
            uprn=uprn,
            ppsf_data=ppsf_data,
            bargain_score=bargain_score,
            comparables=comparables,
            calculated_at=datetime.utcnow(),
        )

        # Persist to database
        if persist:
            await self._persist_metrics(property_obj, analysis)

        logger.info(
            f"Analyzed {uprn}: PPSF={ppsf_data.asking_ppsf:.0f}, "
            f"discount={ppsf_data.discount_pct:.1%}" if ppsf_data.discount_pct else f"Analyzed {uprn}: PPSF={ppsf_data.asking_ppsf:.0f}"
        )

        return analysis

    async def analyze_postcode_district(
        self,
        postcode_district: str,
        persist: bool = True,
    ) -> List[PropertyAnalysis]:
        """
        Analyze all properties in a postcode district.

        Args:
            postcode_district: Postcode prefix (e.g., "SW15")
            persist: Whether to save results

        Returns:
            List of PropertyAnalysis for all analyzed properties
        """
        # Find all properties with active listings in the district
        result = await self.db.execute(
            select(Property)
            .where(Property.current_listing_id.isnot(None))
            .where(Property.floor_area_sqft.isnot(None))
            .where(Property.floor_area_sqft > 0)
            .where(
                Property.address_bs7666["postcode"].astext.startswith(postcode_district)
            )
        )
        properties = result.scalars().all()

        logger.info(f"Analyzing {len(properties)} properties in {postcode_district}")

        analyses = []
        for prop in properties:
            try:
                analysis = await self.analyze_property(prop.uprn, persist=persist)
                if analysis:
                    analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze {prop.uprn}: {e}")
                continue

        logger.info(
            f"Completed analysis for {len(analyses)}/{len(properties)} properties"
        )

        return analyses

    async def _persist_metrics(
        self,
        property_obj: Property,
        analysis: PropertyAnalysis,
    ) -> None:
        """Persist analysis results to ValuationMetrics table."""
        # Check for existing metrics
        result = await self.db.execute(
            select(ValuationMetrics)
            .where(ValuationMetrics.uprn == property_obj.uprn)
        )
        existing = result.scalar_one_or_none()

        # Map priority enum
        priority_map = {
            "High": DBPriority.HIGH,
            "Medium": DBPriority.MEDIUM,
            "Low": DBPriority.LOW,
        }
        db_priority = priority_map.get(
            analysis.bargain_score.priority.value,
            DBPriority.LOW,
        )

        if existing:
            # Update existing
            existing.current_ppsf = analysis.ppsf_data.asking_ppsf
            existing.market_ppsf_12m = analysis.ppsf_data.market_ppsf
            existing.undervalued_index = analysis.ppsf_data.discount_pct
            existing.projected_yield = analysis.bargain_score.projected_yield
            existing.comparable_count = analysis.ppsf_data.comparable_count
            existing.priority = db_priority
            existing.calculated_at = analysis.calculated_at
        else:
            # Create new
            metrics = ValuationMetrics(
                id=uuid4(),
                uprn=property_obj.uprn,
                current_ppsf=analysis.ppsf_data.asking_ppsf,
                market_ppsf_12m=analysis.ppsf_data.market_ppsf,
                undervalued_index=analysis.ppsf_data.discount_pct,
                projected_yield=analysis.bargain_score.projected_yield,
                comparable_count=analysis.ppsf_data.comparable_count,
                priority=db_priority,
                calculated_at=analysis.calculated_at,
            )
            self.db.add(metrics)

        await self.db.flush()
