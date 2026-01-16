"""PPSF Calculator - Price Per Square Foot calculations.

Core component of the analysis engine that calculates and compares
price per square foot metrics.
"""

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class PPSFData:
    """PPSF calculation result."""

    asking_ppsf: float  # Current asking price per sqft
    market_ppsf: Optional[float]  # Market average PPSF (from comparables)
    discount_pct: Optional[float]  # Percentage below market (positive = undervalued)
    comparable_count: int  # Number of comparables used
    confidence_score: float  # 0-1 confidence in the calculation


@dataclass
class ComparableProperty:
    """A comparable property used in PPSF calculations."""

    uprn: Optional[str]
    postcode: str
    property_type: str
    price_paid: float
    floor_area_sqft: float
    transaction_date: date
    ppsf: float  # Calculated PPSF


class PPSFCalculator:
    """
    Calculates Price Per Square Foot (PPSF) metrics.

    The calculator:
    1. Computes asking PPSF from listing price and floor area
    2. Finds comparable transactions in the same postcode sector
    3. Calculates market average PPSF from comparables
    4. Determines discount percentage (undervalued index)

    Example:
        >>> calc = PPSFCalculator()
        >>> result = calc.calculate(
        ...     asking_price=650000,
        ...     floor_area_sqft=1250,
        ...     comparables=comparable_transactions
        ... )
        >>> print(f"Discount: {result.discount_pct:.1%}")
    """

    # Minimum comparables needed for reliable calculation
    MIN_COMPARABLES = 3
    # Maximum age of comparable transactions
    MAX_COMPARABLE_AGE_MONTHS = 24
    # Weight decay for older transactions
    AGE_DECAY_MONTHS = 6

    def __init__(
        self,
        min_comparables: int = 3,
        max_age_months: int = 24,
    ):
        """
        Initialize the calculator.

        Args:
            min_comparables: Minimum comparables for reliable calculation
            max_age_months: Maximum age of transactions to consider
        """
        self.min_comparables = min_comparables
        self.max_age_months = max_age_months

    def calculate(
        self,
        asking_price: float,
        floor_area_sqft: float,
        comparables: List[ComparableProperty],
    ) -> PPSFData:
        """
        Calculate PPSF metrics for a property.

        Args:
            asking_price: Current asking price (GBP)
            floor_area_sqft: Property floor area (sq ft)
            comparables: List of comparable properties with PPSF

        Returns:
            PPSFData with calculated metrics
        """
        if floor_area_sqft <= 0:
            logger.warning("Invalid floor area, cannot calculate PPSF")
            return PPSFData(
                asking_ppsf=0,
                market_ppsf=None,
                discount_pct=None,
                comparable_count=0,
                confidence_score=0,
            )

        # Calculate asking PPSF
        asking_ppsf = asking_price / floor_area_sqft

        # Filter valid comparables
        valid_comparables = self._filter_comparables(comparables)

        if len(valid_comparables) < self.min_comparables:
            logger.debug(
                f"Only {len(valid_comparables)} comparables found, "
                f"need {self.min_comparables} for reliable calculation"
            )
            return PPSFData(
                asking_ppsf=asking_ppsf,
                market_ppsf=None,
                discount_pct=None,
                comparable_count=len(valid_comparables),
                confidence_score=self._calculate_confidence(len(valid_comparables)),
            )

        # Calculate weighted market PPSF
        market_ppsf = self._calculate_market_ppsf(valid_comparables)

        # Calculate discount (positive = below market = undervalued)
        discount_pct = (market_ppsf - asking_ppsf) / market_ppsf if market_ppsf > 0 else None

        return PPSFData(
            asking_ppsf=round(asking_ppsf, 2),
            market_ppsf=round(market_ppsf, 2),
            discount_pct=round(discount_pct, 4) if discount_pct else None,
            comparable_count=len(valid_comparables),
            confidence_score=self._calculate_confidence(len(valid_comparables)),
        )

    def _filter_comparables(
        self,
        comparables: List[ComparableProperty],
    ) -> List[ComparableProperty]:
        """Filter comparables by age and validity."""
        cutoff_date = date.today() - timedelta(days=self.max_age_months * 30)

        valid = []
        for comp in comparables:
            # Must have positive PPSF and be within age limit
            if comp.ppsf > 0 and comp.transaction_date >= cutoff_date:
                valid.append(comp)

        return valid

    def _calculate_market_ppsf(
        self,
        comparables: List[ComparableProperty],
    ) -> float:
        """
        Calculate weighted average market PPSF.

        More recent transactions are weighted higher.
        """
        if not comparables:
            return 0.0

        today = date.today()
        total_weight = 0.0
        weighted_sum = 0.0

        for comp in comparables:
            # Calculate age weight (exponential decay)
            age_days = (today - comp.transaction_date).days
            age_months = age_days / 30

            # Weight decays exponentially with age
            weight = 1.0 / (1.0 + (age_months / self.AGE_DECAY_MONTHS))

            weighted_sum += comp.ppsf * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _calculate_confidence(self, comparable_count: int) -> float:
        """
        Calculate confidence score based on comparable count.

        Returns a score from 0-1 representing confidence in the calculation.
        """
        if comparable_count == 0:
            return 0.0
        elif comparable_count < self.min_comparables:
            return 0.3 * (comparable_count / self.min_comparables)
        elif comparable_count < 10:
            return 0.3 + 0.5 * ((comparable_count - self.min_comparables) / 7)
        else:
            return min(0.8 + 0.02 * (comparable_count - 10), 1.0)

    @staticmethod
    def calculate_single_ppsf(price: float, floor_area_sqft: float) -> Optional[float]:
        """Calculate PPSF for a single transaction."""
        if floor_area_sqft > 0:
            return round(price / floor_area_sqft, 2)
        return None
