"""Bargain Index Calculator - Opportunity scoring algorithm.

Calculates the "undervalued index" that ranks properties by investment potential.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class OpportunityPriority(str, Enum):
    """Priority classification for opportunities."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class BargainScore:
    """Complete bargain analysis score."""

    undervalued_index: float  # Primary score (discount percentage)
    priority: OpportunityPriority
    confidence: float  # 0-1 confidence score
    projected_yield: Optional[float]  # Estimated rental yield
    value_uplift_potential: Optional[float]  # Potential value increase

    # Component scores
    ppsf_score: float  # PPSF discount contribution
    area_score: float  # Area desirability contribution
    condition_score: float  # Property condition contribution


class BargainIndexCalculator:
    """
    Calculates the bargain index (undervalued score) for properties.

    The algorithm considers:
    1. PPSF Discount - How much below market average
    2. Area Metrics - Postcode sector performance
    3. Property Condition - EPC rating, age, etc.
    4. Market Momentum - Price trend in the area

    Priority Classification:
    - HIGH: Undervalued index >= 15% (strong buy signal)
    - MEDIUM: Undervalued index 5-15% (worth investigating)
    - LOW: Undervalued index < 5% (marginal opportunity)

    Example:
        >>> calc = BargainIndexCalculator()
        >>> score = calc.calculate(
        ...     ppsf_discount=0.18,
        ...     comparable_count=12,
        ...     epc_rating="C"
        ... )
        >>> print(f"Priority: {score.priority.value}")
    """

    # Priority thresholds
    HIGH_PRIORITY_THRESHOLD = 0.15  # 15% or more below market
    MEDIUM_PRIORITY_THRESHOLD = 0.05  # 5-15% below market

    # Component weights
    WEIGHT_PPSF = 0.6
    WEIGHT_AREA = 0.25
    WEIGHT_CONDITION = 0.15

    # Average rental yields by property type (UK averages)
    RENTAL_YIELDS = {
        "Flat": 0.052,  # 5.2%
        "Terraced": 0.045,
        "Semi-Detached": 0.042,
        "Detached": 0.038,
    }

    def calculate(
        self,
        ppsf_discount: Optional[float],
        comparable_count: int,
        epc_rating: Optional[str] = None,
        property_type: Optional[str] = None,
        asking_price: Optional[float] = None,
        area_price_trend: Optional[float] = None,  # -1 to 1, positive = rising
    ) -> BargainScore:
        """
        Calculate the bargain score for a property.

        Args:
            ppsf_discount: Discount from market PPSF (0.15 = 15% below)
            comparable_count: Number of comparables used
            epc_rating: EPC rating A-G
            property_type: Detached, Semi-Detached, Terraced, Flat
            asking_price: Current asking price
            area_price_trend: Price trend in area (-1 to 1)

        Returns:
            BargainScore with composite analysis
        """
        # Calculate component scores
        ppsf_score = self._calculate_ppsf_score(ppsf_discount)
        area_score = self._calculate_area_score(area_price_trend)
        condition_score = self._calculate_condition_score(epc_rating)

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(
            ppsf_discount=ppsf_discount,
            comparable_count=comparable_count,
            has_epc=epc_rating is not None,
        )

        # Use PPSF discount as primary undervalued index
        undervalued_index = ppsf_discount if ppsf_discount is not None else 0.0

        # Determine priority
        priority = self._determine_priority(undervalued_index, confidence)

        # Estimate rental yield
        projected_yield = self._estimate_yield(
            property_type=property_type,
            epc_rating=epc_rating,
        )

        # Estimate value uplift potential
        value_uplift = self._estimate_value_uplift(
            undervalued_index=undervalued_index,
            epc_rating=epc_rating,
            area_trend=area_price_trend,
        )

        return BargainScore(
            undervalued_index=round(undervalued_index, 4),
            priority=priority,
            confidence=round(confidence, 2),
            projected_yield=round(projected_yield, 4) if projected_yield else None,
            value_uplift_potential=round(value_uplift, 2) if value_uplift else None,
            ppsf_score=round(ppsf_score, 2),
            area_score=round(area_score, 2),
            condition_score=round(condition_score, 2),
        )

    def _calculate_ppsf_score(self, ppsf_discount: Optional[float]) -> float:
        """Score based on PPSF discount (0-1 scale)."""
        if ppsf_discount is None:
            return 0.0

        # Normalize: 20% discount = score of 1.0
        return min(max(ppsf_discount / 0.20, 0), 1.0)

    def _calculate_area_score(self, area_price_trend: Optional[float]) -> float:
        """Score based on area price trend (0-1 scale)."""
        if area_price_trend is None:
            return 0.5  # Neutral if unknown

        # Positive trend (rising prices) is good for investment
        # Normalize from -1,1 to 0,1
        return (area_price_trend + 1) / 2

    def _calculate_condition_score(self, epc_rating: Optional[str]) -> float:
        """Score based on EPC rating (0-1 scale)."""
        if not epc_rating:
            return 0.5  # Neutral if unknown

        # EPC ratings from A (best) to G (worst)
        ratings = {"A": 1.0, "B": 0.9, "C": 0.75, "D": 0.6, "E": 0.4, "F": 0.2, "G": 0.1}
        return ratings.get(epc_rating.upper(), 0.5)

    def _calculate_confidence(
        self,
        ppsf_discount: Optional[float],
        comparable_count: int,
        has_epc: bool,
    ) -> float:
        """Calculate overall confidence in the score."""
        confidence = 0.0

        # Having PPSF discount is crucial
        if ppsf_discount is not None:
            confidence += 0.4

        # More comparables = higher confidence
        if comparable_count >= 10:
            confidence += 0.35
        elif comparable_count >= 5:
            confidence += 0.25
        elif comparable_count >= 3:
            confidence += 0.15

        # Having EPC data helps
        if has_epc:
            confidence += 0.15

        # Bonus for having all data
        if ppsf_discount is not None and comparable_count >= 5 and has_epc:
            confidence += 0.1

        return min(confidence, 1.0)

    def _determine_priority(
        self,
        undervalued_index: float,
        confidence: float,
    ) -> OpportunityPriority:
        """Determine priority classification."""
        # Adjust threshold based on confidence
        adjusted_index = undervalued_index * confidence

        if undervalued_index >= self.HIGH_PRIORITY_THRESHOLD and confidence >= 0.5:
            return OpportunityPriority.HIGH
        elif undervalued_index >= self.MEDIUM_PRIORITY_THRESHOLD:
            return OpportunityPriority.MEDIUM
        else:
            return OpportunityPriority.LOW

    def _estimate_yield(
        self,
        property_type: Optional[str],
        epc_rating: Optional[str],
    ) -> Optional[float]:
        """Estimate rental yield based on property type and EPC."""
        if not property_type:
            return None

        base_yield = self.RENTAL_YIELDS.get(property_type, 0.045)

        # Adjust for EPC rating (better EPC = higher rents)
        if epc_rating:
            epc_adjustments = {
                "A": 1.10, "B": 1.05, "C": 1.0,
                "D": 0.95, "E": 0.90, "F": 0.85, "G": 0.80,
            }
            base_yield *= epc_adjustments.get(epc_rating.upper(), 1.0)

        return base_yield

    def _estimate_value_uplift(
        self,
        undervalued_index: float,
        epc_rating: Optional[str],
        area_trend: Optional[float],
    ) -> Optional[float]:
        """
        Estimate potential value increase.

        Considers:
        - Current undervaluation (can be corrected)
        - EPC improvement potential
        - Area price momentum
        """
        if undervalued_index <= 0:
            return None

        # Base uplift is the undervaluation itself
        uplift = undervalued_index

        # Add EPC improvement potential (poor EPC = more improvement room)
        if epc_rating:
            epc_potential = {"A": 0, "B": 0.02, "C": 0.04, "D": 0.06, "E": 0.08, "F": 0.10, "G": 0.12}
            uplift += epc_potential.get(epc_rating.upper(), 0)

        # Factor in area momentum
        if area_trend and area_trend > 0:
            uplift += area_trend * 0.05  # Rising area adds potential

        return uplift
