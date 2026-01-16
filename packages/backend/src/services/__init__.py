"""Services package - External service clients and business logic."""

from .address_matcher import AddressComponents, AddressMatcher
from .analysis_service import AnalysisService, PropertyAnalysis
from .bargain_calculator import BargainIndexCalculator, BargainScore, OpportunityPriority
from .comparables_finder import ComparablesFinder, ComparableSearchCriteria
from .epc_client import EPCClient, EPCData, EPCServiceError
from .hmlr_client import HMLRClient, HMLRQueryError, TransactionRecord
from .ppsf_calculator import ComparableProperty, PPSFCalculator, PPSFData

__all__ = [
    # HMLR
    "HMLRClient",
    "HMLRQueryError",
    "TransactionRecord",
    # EPC
    "EPCClient",
    "EPCData",
    "EPCServiceError",
    # Address Matching
    "AddressMatcher",
    "AddressComponents",
    # PPSF Calculator
    "PPSFCalculator",
    "PPSFData",
    "ComparableProperty",
    # Bargain Calculator
    "BargainIndexCalculator",
    "BargainScore",
    "OpportunityPriority",
    # Comparables
    "ComparablesFinder",
    "ComparableSearchCriteria",
    # Analysis Service
    "AnalysisService",
    "PropertyAnalysis",
]
