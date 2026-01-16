"""Base scraper interface and common utilities.

All property portal scrapers inherit from this base class.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScrapedListing:
    """Represents a scraped property listing."""

    external_url: str
    asking_price: float
    address_raw: str
    postcode: str
    listing_date: date
    agent_name: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floor_area_sqft: Optional[float] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    raw_data: Optional[dict] = None


class BaseScraper(ABC):
    """
    Abstract base class for property portal scrapers.

    All scrapers must implement the search() method and respect:
    - Rate limiting
    - robots.txt compliance
    - Error handling with retries

    Example:
        >>> scraper = RightmoveScraper()
        >>> if await scraper.check_robots_compliance():
        ...     listings = await scraper.search("SW15")
    """

    # Must be set by subclasses
    PORTAL_NAME: str = "Unknown"
    BASE_URL: str = ""
    ROBOTS_URL: str = ""

    def __init__(
        self,
        rate_limit: float = 2.0,
        headless: bool = True,
        user_agent: Optional[str] = None,
    ):
        """
        Initialize the scraper.

        Args:
            rate_limit: Requests per second limit
            headless: Run browser in headless mode
            user_agent: Custom user agent string
        """
        self.rate_limit = rate_limit
        self.headless = headless
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; UndervaluedBot/1.0; "
            "+https://github.com/undervalued)"
        )
        self._last_request_time: float = 0

    @abstractmethod
    async def search(
        self,
        postcode_district: str,
        property_types: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        max_results: int = 50,
    ) -> List[ScrapedListing]:
        """
        Search for property listings.

        Args:
            postcode_district: Postcode prefix (e.g., "SW15")
            property_types: Filter by property types
            min_price: Minimum price filter
            max_price: Maximum price filter
            max_results: Maximum listings to return

        Returns:
            List of ScrapedListing objects
        """
        pass

    @abstractmethod
    async def get_listing_details(self, url: str) -> Optional[ScrapedListing]:
        """
        Get detailed information for a specific listing.

        Args:
            url: Listing URL

        Returns:
            ScrapedListing with full details, or None if failed
        """
        pass

    async def check_robots_compliance(self, path: str = "/") -> bool:
        """
        Check if scraping a path is allowed by robots.txt.

        Args:
            path: URL path to check

        Returns:
            True if scraping is allowed
        """
        # TODO: Implement actual robots.txt parsing
        # For now, return False to prevent unauthorized scraping
        logger.warning(
            f"robots.txt compliance check not implemented for {self.PORTAL_NAME}"
        )
        return False

    async def _rate_limit_wait(self) -> None:
        """Wait to respect rate limiting."""
        import asyncio
        import time

        now = time.time()
        min_interval = 1.0 / self.rate_limit
        elapsed = now - self._last_request_time

        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)

        self._last_request_time = time.time()


class ScraperError(Exception):
    """Base exception for scraper errors."""

    pass


class RateLimitError(ScraperError):
    """Raised when rate limited by the portal."""

    pass


class BlockedError(ScraperError):
    """Raised when scraper is blocked."""

    pass
