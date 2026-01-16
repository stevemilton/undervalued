"""Properties API endpoints - GET /api/v1/properties/{uprn}/analysis."""

from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ...models import Property, HistoricalTransaction, ValuationMetrics
from ...schemas import (
    AddressBS7666,
    ChartDataPoint,
    ComparableTransaction,
    ListingInOpportunity,
    MetricsResponse,
    PropertyResponse,
    TransactionWithPPSF,
)
from ..deps import DbSession

router = APIRouter(prefix="/properties", tags=["properties"])


class PropertyAnalysisResponse:
    """Response model for property analysis endpoint."""

    pass


from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PropertyAnalysisResponse(BaseModel):
    """Full property analysis response."""

    property: PropertyResponse
    current_listing: Optional[ListingInOpportunity] = None
    metrics: Optional[MetricsResponse] = None
    historical_transactions: List[TransactionWithPPSF]
    comparables: List[ComparableTransaction]
    chart_data: dict


@router.get("/{uprn}/analysis", response_model=PropertyAnalysisResponse)
async def get_property_analysis(
    db: DbSession,
    uprn: str,
) -> PropertyAnalysisResponse:
    """
    Get deep-dive analysis for a specific property.

    Returns:
    - Property details
    - Current listing (if on market)
    - Valuation metrics
    - Historical transactions for this property
    - Comparable transactions in the area
    - Chart data for visualization
    """
    # Fetch property with relationships
    query = (
        select(Property)
        .where(Property.uprn == uprn)
        .options(
            selectinload(Property.current_listing),
            selectinload(Property.valuation_metrics),
            selectinload(Property.historical_transactions),
        )
    )
    result = await db.execute(query)
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with UPRN '{uprn}' not found",
        )

    # Build property response
    property_response = PropertyResponse(
        uprn=property_obj.uprn,
        address_bs7666=AddressBS7666(**property_obj.address_bs7666),
        floor_area_sqft=property_obj.floor_area_sqft,
        property_type=property_obj.property_type.value if hasattr(property_obj.property_type, 'value') else property_obj.property_type,
        epc_rating=property_obj.epc_rating,
        current_listing_id=property_obj.current_listing_id,
    )

    # Build listing response if exists
    listing_response = None
    if property_obj.current_listing:
        listing = property_obj.current_listing
        listing_response = ListingInOpportunity(
            listing_id=listing.listing_id,
            external_url=listing.external_url,
            asking_price=listing.asking_price,
            listing_date=listing.listing_date,
            agent_name=listing.agent_name,
            source=listing.source,
        )

    # Build metrics response if exists
    metrics_response = None
    if property_obj.valuation_metrics:
        metrics = property_obj.valuation_metrics
        metrics_response = MetricsResponse(
            id=metrics.id,
            uprn=metrics.uprn,
            current_ppsf=metrics.current_ppsf,
            market_ppsf_12m=metrics.market_ppsf_12m,
            undervalued_index=metrics.undervalued_index,
            projected_yield=metrics.projected_yield,
            comparable_count=metrics.comparable_count,
            priority=metrics.priority.value if hasattr(metrics.priority, 'value') else metrics.priority,
            calculated_at=metrics.calculated_at,
        )

    # Build historical transactions with PPSF
    historical = []
    for tx in property_obj.historical_transactions:
        ppsf = None
        if property_obj.floor_area_sqft and property_obj.floor_area_sqft > 0:
            ppsf = float(tx.price_paid) / property_obj.floor_area_sqft
        historical.append(
            TransactionWithPPSF(
                transaction_id=tx.transaction_id,
                uprn=tx.uprn,
                price_paid=tx.price_paid,
                date_of_transfer=tx.date_of_transfer,
                transaction_category=tx.transaction_category.value if hasattr(tx.transaction_category, 'value') else tx.transaction_category,
                price_per_sqft=ppsf,
                floor_area_sqft=property_obj.floor_area_sqft,
            )
        )

    # TODO: Fetch comparables from same postcode sector
    # This will be implemented in Step 5 (Analysis Engine)
    comparables: List[ComparableTransaction] = []

    # Build chart data
    chart_data = {
        "scatter_plot": [
            ChartDataPoint(
                x=tx.date_of_transfer.isoformat(),
                y=tx.price_per_sqft or 0,
                label=f"UPRN {tx.uprn}",
                is_subject=True,
            ).model_dump()
            for tx in historical
            if tx.price_per_sqft
        ]
    }

    return PropertyAnalysisResponse(
        property=property_response,
        current_listing=listing_response,
        metrics=metrics_response,
        historical_transactions=historical,
        comparables=comparables,
        chart_data=chart_data,
    )
