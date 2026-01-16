"""System API endpoints - POST /api/v1/system/ingest."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/system", tags=["system"])


class IngestionRequest(BaseModel):
    """Request body for triggering data ingestion."""

    source: str = Field(
        default="all",
        description="Data source: 'rightmove', 'zoopla', 'hmlr', or 'all'",
    )
    postcode_districts: Optional[List[str]] = Field(
        None,
        description="Limit ingestion to specific postcode districts",
    )
    force_refresh: bool = Field(
        default=False,
        description="Re-scrape even if data already exists",
    )


class IngestionResponse(BaseModel):
    """Response for ingestion trigger."""

    task_id: str
    status: str
    estimated_completion: datetime


async def run_ingestion_task(
    task_id: str,
    source: str,
    postcode_districts: Optional[List[str]],
    force_refresh: bool,
) -> None:
    """
    Background task for running data ingestion.

    NOTE: This is a placeholder. Full implementation will be in Step 7 (Celery Tasks).
    """
    # TODO: Implement actual ingestion logic
    # - Scrape listings from Rightmove/Zoopla
    # - Query HMLR for historical transactions
    # - Match addresses to UPRNs
    # - Calculate valuation metrics
    pass


@router.post("/ingest", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
) -> IngestionResponse:
    """
    Trigger data ingestion pipeline.

    This is an admin-only endpoint that initiates:
    1. Scraping new listings from property portals
    2. Querying Land Registry for recent transactions
    3. Matching and storing data
    4. Computing valuation metrics

    The task runs in the background and returns immediately.
    """
    # Generate task ID
    task_id = str(uuid4())[:8]

    # Estimate completion time (placeholder)
    estimated_completion = datetime.utcnow() + timedelta(minutes=15)

    # Add background task
    background_tasks.add_task(
        run_ingestion_task,
        task_id=task_id,
        source=request.source,
        postcode_districts=request.postcode_districts,
        force_refresh=request.force_refresh,
    )

    return IngestionResponse(
        task_id=task_id,
        status="queued",
        estimated_completion=estimated_completion,
    )


class SystemStatus(BaseModel):
    """System health status."""

    database: str
    redis: str
    last_ingestion: Optional[datetime] = None
    total_properties: int
    total_opportunities: int


@router.get("/status", response_model=SystemStatus)
async def get_system_status() -> SystemStatus:
    """
    Get current system status.

    Returns connection status for database and redis,
    plus statistics about data in the system.
    """
    # TODO: Implement actual health checks
    return SystemStatus(
        database="connected",
        redis="connected",
        last_ingestion=None,
        total_properties=0,
        total_opportunities=0,
    )
