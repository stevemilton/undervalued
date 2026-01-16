"""Opportunities API endpoints - GET /api/v1/opportunities."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models import Property, ActiveListing, ValuationMetrics
from ...schemas import (
    OpportunityFilters,
    OpportunityItem,
    PaginatedResponse,
    AddressBS7666,
    ListingInOpportunity,
    MetricsInOpportunity,
)
from ..deps import DbSession, Pagination

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=PaginatedResponse[OpportunityItem])
async def list_opportunities(
    db: DbSession,
    pagination: Pagination,
    postcode_district: Annotated[str, Query(min_length=2, max_length=4, pattern=r"^[A-Z]{1,2}[0-9]{1,2}[A-Z]?$")],
    min_discount_pct: Annotated[Optional[float], Query(ge=0, le=1)] = None,
    max_price: Annotated[Optional[float], Query(gt=0)] = None,
    property_types: Annotated[Optional[List[str]], Query()] = None,
    sort_by: str = "undervalued_index_desc",
) -> PaginatedResponse[OpportunityItem]:
    """
    Retrieve paginated list of undervalued properties.

    Filters properties by postcode district and applies optional filters:
    - min_discount_pct: Minimum undervalued index (0.1 = 10% below market)
    - max_price: Maximum asking price in GBP
    - property_types: Filter by property types (Detached, Semi-Detached, Terraced, Flat)
    - sort_by: Sorting field (undervalued_index_desc, price_asc, etc.)
    """
    page = pagination["page"]
    per_page = pagination["per_page"]

    # Build base query with joins
    query = (
        select(Property)
        .join(ActiveListing, Property.current_listing_id == ActiveListing.listing_id)
        .join(ValuationMetrics, Property.uprn == ValuationMetrics.uprn)
        .options(
            selectinload(Property.current_listing),
            selectinload(Property.valuation_metrics),
        )
    )

    # Apply postcode filter using JSONB
    query = query.where(
        Property.address_bs7666["postcode"].astext.startswith(postcode_district)
    )

    # Apply optional filters
    if min_discount_pct is not None:
        query = query.where(ValuationMetrics.undervalued_index >= min_discount_pct)

    if max_price is not None:
        query = query.where(ActiveListing.asking_price <= max_price)

    if property_types:
        query = query.where(Property.property_type.in_(property_types))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    if sort_by == "undervalued_index_desc":
        query = query.order_by(ValuationMetrics.undervalued_index.desc().nullslast())
    elif sort_by == "price_asc":
        query = query.order_by(ActiveListing.asking_price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(ActiveListing.asking_price.desc())
    else:
        query = query.order_by(ValuationMetrics.undervalued_index.desc().nullslast())

    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute query
    result = await db.execute(query)
    properties = result.scalars().all()

    # Transform to response items
    items = []
    for prop in properties:
        listing = prop.current_listing
        metrics = prop.valuation_metrics

        if listing and metrics:
            items.append(
                OpportunityItem(
                    uprn=prop.uprn,
                    address=AddressBS7666(**prop.address_bs7666),
                    property_type=prop.property_type.value if hasattr(prop.property_type, 'value') else prop.property_type,
                    floor_area_sqft=prop.floor_area_sqft,
                    epc_rating=prop.epc_rating,
                    listing=ListingInOpportunity(
                        listing_id=listing.listing_id,
                        external_url=listing.external_url,
                        asking_price=listing.asking_price,
                        listing_date=listing.listing_date,
                        agent_name=listing.agent_name,
                        source=listing.source,
                    ),
                    metrics=MetricsInOpportunity(
                        current_ppsf=metrics.current_ppsf,
                        market_ppsf_12m=metrics.market_ppsf_12m,
                        undervalued_index=metrics.undervalued_index,
                        projected_yield=metrics.projected_yield,
                        comparable_count=metrics.comparable_count,
                        priority=metrics.priority.value if hasattr(metrics.priority, 'value') else metrics.priority,
                        calculated_at=metrics.calculated_at,
                    ),
                )
            )

    return PaginatedResponse.create(items=items, total=total, page=page, per_page=per_page)
