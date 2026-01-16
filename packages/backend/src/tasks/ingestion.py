"""Data ingestion background tasks.

These tasks handle:
1. Scraping listings from property portals
2. Querying Land Registry for transactions
3. Running analysis on new/updated properties
"""

import logging
from datetime import datetime
from typing import List, Optional

from celery import shared_task

from ..models.base import async_session_factory
from ..scrapers import get_sample_listings
from ..services import AnalysisService, HMLRClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def ingest_postcode_district(
    self,
    postcode_district: str,
    source: str = "all",
    force_refresh: bool = False,
) -> dict:
    """
    Ingest and analyze properties for a postcode district.

    This is the main ingestion task that:
    1. Scrapes new listings (placeholder - uses sample data)
    2. Queries Land Registry for transactions
    3. Matches addresses to UPRNs
    4. Runs analysis and stores metrics

    Args:
        postcode_district: e.g., "SW15"
        source: "rightmove", "zoopla", or "all"
        force_refresh: Re-process even if data exists

    Returns:
        Summary of ingestion results
    """
    import asyncio

    logger.info(f"Starting ingestion for {postcode_district}")

    try:
        result = asyncio.run(
            _run_ingestion(postcode_district, source, force_refresh)
        )
        return result
    except Exception as e:
        logger.error(f"Ingestion failed for {postcode_district}: {e}")
        raise self.retry(exc=e, countdown=60)


async def _run_ingestion(
    postcode_district: str,
    source: str,
    force_refresh: bool,
) -> dict:
    """Async implementation of ingestion."""
    stats = {
        "postcode_district": postcode_district,
        "started_at": datetime.utcnow().isoformat(),
        "listings_found": 0,
        "properties_analyzed": 0,
        "errors": 0,
    }

    # Get sample listings (placeholder for real scraping)
    listings = get_sample_listings(postcode_district)
    stats["listings_found"] = len(listings)
    logger.info(f"Found {len(listings)} listings in {postcode_district}")

    # Query Land Registry for transactions
    hmlr_client = HMLRClient()
    try:
        # Extract postcode sector from district
        postcode_sector = f"{postcode_district} 1"  # Default to sector 1
        transactions = await hmlr_client.query_transactions(
            postcode_sector=postcode_sector,
            limit=100,
        )
        stats["transactions_found"] = len(transactions)
        logger.info(f"Found {len(transactions)} Land Registry transactions")
    except Exception as e:
        logger.warning(f"HMLR query failed: {e}")
        stats["transactions_found"] = 0

    # Run analysis for properties with listings
    async with async_session_factory() as db:
        analysis_service = AnalysisService(db)

        try:
            analyses = await analysis_service.analyze_postcode_district(
                postcode_district=postcode_district,
                persist=True,
            )
            stats["properties_analyzed"] = len(analyses)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            stats["errors"] += 1

        await db.commit()

    stats["completed_at"] = datetime.utcnow().isoformat()
    logger.info(f"Ingestion complete: {stats}")

    return stats


@shared_task
def refresh_all_opportunities() -> dict:
    """
    Periodic task to refresh all opportunity data.

    Runs daily to update metrics for all active listings.
    """
    import asyncio

    logger.info("Starting daily opportunity refresh")

    return asyncio.run(_refresh_all())


async def _refresh_all() -> dict:
    """Refresh metrics for all properties with active listings."""
    stats = {
        "started_at": datetime.utcnow().isoformat(),
        "properties_refreshed": 0,
    }

    async with async_session_factory() as db:
        analysis_service = AnalysisService(db)

        # Get unique postcode districts with active listings
        # This is a simplified approach - production would batch by district
        from sqlalchemy import select, func
        from ..models import Property

        result = await db.execute(
            select(
                func.left(
                    Property.address_bs7666["postcode"].astext, 4
                ).label("district")
            )
            .where(Property.current_listing_id.isnot(None))
            .group_by("district")
        )
        districts = [row[0] for row in result.fetchall()]

        for district in districts:
            try:
                analyses = await analysis_service.analyze_postcode_district(
                    postcode_district=district.strip(),
                    persist=True,
                )
                stats["properties_refreshed"] += len(analyses)
            except Exception as e:
                logger.error(f"Refresh failed for {district}: {e}")

        await db.commit()

    stats["completed_at"] = datetime.utcnow().isoformat()
    logger.info(f"Refresh complete: {stats}")

    return stats


@shared_task
def analyze_single_property(uprn: str) -> dict:
    """
    Analyze a single property on demand.

    Useful for immediate analysis after a new listing is added.

    Args:
        uprn: Property UPRN to analyze

    Returns:
        Analysis summary
    """
    import asyncio

    return asyncio.run(_analyze_single(uprn))


async def _analyze_single(uprn: str) -> dict:
    """Async single property analysis."""
    async with async_session_factory() as db:
        analysis_service = AnalysisService(db)
        analysis = await analysis_service.analyze_property(uprn, persist=True)
        await db.commit()

        if analysis:
            return {
                "uprn": uprn,
                "success": True,
                "undervalued_index": analysis.bargain_score.undervalued_index,
                "priority": analysis.bargain_score.priority.value,
            }
        else:
            return {
                "uprn": uprn,
                "success": False,
                "error": "Property not found or missing data",
            }
