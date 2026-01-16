"""Tests for analysis engine components."""

from datetime import date, timedelta

import pytest

from src.services.bargain_calculator import BargainIndexCalculator, OpportunityPriority
from src.services.ppsf_calculator import ComparableProperty, PPSFCalculator


class TestPPSFCalculator:
    """Tests for PPSF Calculator."""

    def test_calculate_asking_ppsf(self):
        """Test basic PPSF calculation."""
        calc = PPSFCalculator()
        result = calc.calculate(
            asking_price=500000,
            floor_area_sqft=1000,
            comparables=[],
        )

        assert result.asking_ppsf == 500.0
        assert result.market_ppsf is None
        assert result.discount_pct is None

    def test_calculate_with_comparables(self):
        """Test PPSF with comparable transactions."""
        calc = PPSFCalculator()

        comparables = [
            ComparableProperty(
                uprn="test1",
                postcode="SW15 6EJ",
                property_type="Terraced",
                price_paid=550000,
                floor_area_sqft=1000,
                transaction_date=date.today() - timedelta(days=30),
                ppsf=550.0,
            ),
            ComparableProperty(
                uprn="test2",
                postcode="SW15 6AB",
                property_type="Terraced",
                price_paid=520000,
                floor_area_sqft=1000,
                transaction_date=date.today() - timedelta(days=60),
                ppsf=520.0,
            ),
            ComparableProperty(
                uprn="test3",
                postcode="SW15 6CD",
                property_type="Terraced",
                price_paid=480000,
                floor_area_sqft=1000,
                transaction_date=date.today() - timedelta(days=90),
                ppsf=480.0,
            ),
        ]

        # Asking at 450 PPSF when market is ~520
        result = calc.calculate(
            asking_price=450000,
            floor_area_sqft=1000,
            comparables=comparables,
        )

        assert result.asking_ppsf == 450.0
        assert result.market_ppsf is not None
        assert result.market_ppsf > 450.0  # Market should be higher
        assert result.discount_pct is not None
        assert result.discount_pct > 0  # Should show undervalued

    def test_invalid_floor_area(self):
        """Test handling of invalid floor area."""
        calc = PPSFCalculator()
        result = calc.calculate(
            asking_price=500000,
            floor_area_sqft=0,
            comparables=[],
        )

        assert result.asking_ppsf == 0
        assert result.confidence_score == 0

    def test_single_ppsf_calculation(self):
        """Test static PPSF calculation."""
        assert PPSFCalculator.calculate_single_ppsf(500000, 1000) == 500.0
        assert PPSFCalculator.calculate_single_ppsf(500000, 0) is None


class TestBargainCalculator:
    """Tests for Bargain Index Calculator."""

    def test_high_priority_detection(self):
        """Test HIGH priority for significant discount."""
        calc = BargainIndexCalculator()
        result = calc.calculate(
            ppsf_discount=0.20,  # 20% below market
            comparable_count=15,
            epc_rating="C",
            property_type="Terraced",
        )

        assert result.priority == OpportunityPriority.HIGH
        assert result.undervalued_index == 0.2

    def test_medium_priority_detection(self):
        """Test MEDIUM priority for moderate discount."""
        calc = BargainIndexCalculator()
        result = calc.calculate(
            ppsf_discount=0.08,  # 8% below market
            comparable_count=10,
            epc_rating="D",
        )

        assert result.priority == OpportunityPriority.MEDIUM

    def test_low_priority_detection(self):
        """Test LOW priority for minimal discount."""
        calc = BargainIndexCalculator()
        result = calc.calculate(
            ppsf_discount=0.02,  # Only 2% below
            comparable_count=5,
        )

        assert result.priority == OpportunityPriority.LOW

    def test_yield_estimation(self):
        """Test rental yield estimation."""
        calc = BargainIndexCalculator()
        result = calc.calculate(
            ppsf_discount=0.10,
            comparable_count=10,
            property_type="Flat",
            epc_rating="B",
        )

        assert result.projected_yield is not None
        assert result.projected_yield > 0.04  # Flat yield with good EPC

    def test_confidence_scoring(self):
        """Test confidence score calculation."""
        calc = BargainIndexCalculator()

        # High confidence: all data available
        result_high = calc.calculate(
            ppsf_discount=0.15,
            comparable_count=20,
            epc_rating="C",
        )

        # Low confidence: missing data
        result_low = calc.calculate(
            ppsf_discount=None,
            comparable_count=2,
            epc_rating=None,
        )

        assert result_high.confidence > result_low.confidence

    def test_value_uplift_estimation(self):
        """Test value uplift potential calculation."""
        calc = BargainIndexCalculator()
        result = calc.calculate(
            ppsf_discount=0.15,
            comparable_count=10,
            epc_rating="E",  # Poor EPC = improvement potential
            area_price_trend=0.5,  # Rising area
        )

        assert result.value_uplift_potential is not None
        # Should be at least the discount + EPC potential
        assert result.value_uplift_potential > 0.15
