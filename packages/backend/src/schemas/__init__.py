"""Schemas package - Pydantic request/response models."""

from .common import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    PaginationParams,
)
from .listing import (
    ListingCreate,
    ListingInOpportunity,
    ListingResponse,
    ListingUpdate,
)
from .metrics import (
    ChartDataPoint,
    MetricsInOpportunity,
    MetricsResponse,
    OpportunityFilters,
    OpportunityItem,
)
from .property import (
    AddressBS7666,
    PropertyCreate,
    PropertyInList,
    PropertyResponse,
    PropertyUpdate,
)
from .transaction import (
    ComparableTransaction,
    TransactionCreate,
    TransactionResponse,
    TransactionWithPPSF,
)

__all__ = [
    # Common
    "PaginatedResponse",
    "PaginationParams",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    # Property
    "AddressBS7666",
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyResponse",
    "PropertyInList",
    # Transaction
    "TransactionCreate",
    "TransactionResponse",
    "TransactionWithPPSF",
    "ComparableTransaction",
    # Listing
    "ListingCreate",
    "ListingUpdate",
    "ListingResponse",
    "ListingInOpportunity",
    # Metrics & Opportunities
    "MetricsResponse",
    "MetricsInOpportunity",
    "OpportunityItem",
    "OpportunityFilters",
    "ChartDataPoint",
]
