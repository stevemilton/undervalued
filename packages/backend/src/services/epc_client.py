"""EPC (Energy Performance Certificate) API Client.

Queries the UK EPC Register API to get floor area and energy ratings.
See: https://epc.opendatacommunities.org/docs/api
"""

import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class EPCData:
    """EPC data for a property."""

    lmk_key: str  # Unique EPC certificate key
    address: str
    postcode: str
    floor_area_sqm: float
    floor_area_sqft: float  # Calculated from sqm
    current_energy_rating: str  # A-G
    potential_energy_rating: str
    property_type: Optional[str] = None
    built_form: Optional[str] = None  # Detached, Semi-Detached, etc.
    construction_age_band: Optional[str] = None


class EPCClient:
    """
    Client for querying the UK EPC Register API.

    The EPC Register provides energy performance data including floor area,
    which is essential for calculating price per square foot.

    Note: Requires an API key from https://epc.opendatacommunities.org/

    Example:
        >>> client = EPCClient(api_key="your-api-key")
        >>> epc = await client.get_by_postcode("SW15 6EJ")
    """

    BASE_URL = "https://epc.opendatacommunities.org/api/v1"
    SQM_TO_SQFT = 10.7639  # Conversion factor

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """Initialize the EPC client.

        Args:
            api_key: EPC API key (defaults to settings.epc_api_key)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.epc_api_key
        self.base_url = settings.epc_api_url or self.BASE_URL
        self.timeout = timeout

        if not self.api_key:
            logger.warning("EPC API key not configured - EPC lookups will fail")

    async def get_by_address(
        self,
        postcode: str,
        address_line: Optional[str] = None,
    ) -> Optional[EPCData]:
        """
        Get EPC data by address.

        Args:
            postcode: UK postcode
            address_line: Optional address line for more precise matching

        Returns:
            EPCData if found, None otherwise
        """
        if not self.api_key:
            logger.debug("No EPC API key configured")
            return None

        # Build query parameters
        params = {"postcode": postcode.replace(" ", "")}
        if address_line:
            params["address"] = address_line

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/domestic/search",
                    params=params,
                    headers={
                        "Authorization": f"Basic {self.api_key}",
                        "Accept": "application/json",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    rows = data.get("rows", [])
                    if rows:
                        # Return the most recent EPC (first in results)
                        return self._parse_epc_row(rows[0])

                elif response.status_code == 401:
                    logger.error("EPC API authentication failed - check API key")
                elif response.status_code == 404:
                    logger.debug(f"No EPC found for postcode: {postcode}")
                else:
                    logger.warning(
                        f"EPC API returned status {response.status_code}: {response.text}"
                    )

        except httpx.TimeoutException:
            logger.warning(f"EPC API timeout for postcode: {postcode}")
        except Exception as e:
            logger.error(f"EPC API error: {e}")

        return None

    async def get_floor_area(
        self,
        postcode: str,
        address_line: Optional[str] = None,
    ) -> Optional[float]:
        """
        Get floor area in square feet for an address.

        This is a convenience method that returns just the floor area,
        which is the main data needed for PPSF calculations.

        Args:
            postcode: UK postcode
            address_line: Optional address line for matching

        Returns:
            Floor area in square feet, or None if not found
        """
        epc = await self.get_by_address(postcode, address_line)
        if epc:
            return epc.floor_area_sqft
        return None

    def _parse_epc_row(self, row: dict) -> EPCData:
        """Parse a single EPC row from the API response."""
        floor_area_sqm = float(row.get("total-floor-area", 0) or 0)
        floor_area_sqft = floor_area_sqm * self.SQM_TO_SQFT

        return EPCData(
            lmk_key=row.get("lmk-key", ""),
            address=row.get("address", ""),
            postcode=row.get("postcode", ""),
            floor_area_sqm=floor_area_sqm,
            floor_area_sqft=round(floor_area_sqft, 2),
            current_energy_rating=row.get("current-energy-rating", ""),
            potential_energy_rating=row.get("potential-energy-rating", ""),
            property_type=row.get("property-type"),
            built_form=row.get("built-form"),
            construction_age_band=row.get("construction-age-band"),
        )


class EPCServiceError(Exception):
    """Exception raised when EPC API request fails."""

    pass
