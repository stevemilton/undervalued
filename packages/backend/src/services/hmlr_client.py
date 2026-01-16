"""HM Land Registry SPARQL Client.

Queries the Land Registry Price Paid Data via their public SPARQL endpoint.
See: https://landregistry.data.gov.uk/
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

import httpx
from SPARQLWrapper import JSON, SPARQLWrapper

logger = logging.getLogger(__name__)


@dataclass
class TransactionRecord:
    """Represents a Land Registry transaction record."""

    address_uri: str
    price_paid: float
    transaction_date: date
    property_type: str
    postcode: str
    paon: Optional[str] = None  # Primary Addressable Object Name (house number)
    saon: Optional[str] = None  # Secondary Addressable Object Name (flat number)
    street: Optional[str] = None
    town: Optional[str] = None


class HMLRClient:
    """
    Client for querying HM Land Registry Price Paid Data via SPARQL.

    The Land Registry provides a free public SPARQL endpoint for querying
    historical property transaction data.

    Example:
        >>> client = HMLRClient()
        >>> transactions = await client.query_transactions(
        ...     postcode_sector="SW15 1",
        ...     property_type="Terraced",
        ...     min_date=date(2024, 1, 1)
        ... )
    """

    SPARQL_ENDPOINT = "https://landregistry.data.gov.uk/landregistry/query"

    # Property type mappings from Land Registry URIs
    PROPERTY_TYPE_URIS = {
        "Detached": "http://landregistry.data.gov.uk/def/common/detached",
        "Semi-Detached": "http://landregistry.data.gov.uk/def/common/semi-detached",
        "Terraced": "http://landregistry.data.gov.uk/def/common/terraced",
        "Flat": "http://landregistry.data.gov.uk/def/common/flat-maisonette",
    }

    def __init__(self, timeout: int = 30):
        """Initialize the HMLR client.

        Args:
            timeout: Query timeout in seconds
        """
        self.timeout = timeout
        self._sparql = SPARQLWrapper(self.SPARQL_ENDPOINT)
        self._sparql.setReturnFormat(JSON)
        self._sparql.setTimeout(timeout)

    async def query_transactions(
        self,
        postcode_sector: str,
        property_type: Optional[str] = None,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        limit: int = 500,
    ) -> List[TransactionRecord]:
        """
        Query historical transactions from HM Land Registry.

        Uses postcode SECTOR (e.g., "SW15 1") for optimized query performance.

        Args:
            postcode_sector: Postcode sector like "SW15 1" (outward + first digit of inward)
            property_type: Filter by type (Detached, Semi-Detached, Terraced, Flat)
            min_date: Earliest transaction date to include
            max_date: Latest transaction date to include
            limit: Maximum number of results

        Returns:
            List of TransactionRecord objects
        """
        query = self._build_query(
            postcode_sector=postcode_sector,
            property_type=property_type,
            min_date=min_date,
            max_date=max_date,
            limit=limit,
        )

        logger.debug(f"Executing SPARQL query for postcode sector: {postcode_sector}")

        try:
            # Execute query (SPARQLWrapper is synchronous, so we run it directly)
            self._sparql.setQuery(query)
            results = self._sparql.query().convert()

            transactions = self._parse_results(results)
            logger.info(
                f"Retrieved {len(transactions)} transactions for {postcode_sector}"
            )
            return transactions

        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            raise HMLRQueryError(f"Failed to query Land Registry: {e}") from e

    def _build_query(
        self,
        postcode_sector: str,
        property_type: Optional[str],
        min_date: Optional[date],
        max_date: Optional[date],
        limit: int,
    ) -> str:
        """Build SPARQL query for transaction lookup."""

        # Build property type filter
        type_filter = ""
        if property_type and property_type in self.PROPERTY_TYPE_URIS:
            type_uri = self.PROPERTY_TYPE_URIS[property_type]
            type_filter = f"FILTER(?propertyType = <{type_uri}>)"

        # Build date filters
        date_filters = []
        if min_date:
            date_filters.append(
                f'FILTER(?transactionDate >= "{min_date.isoformat()}"^^xsd:date)'
            )
        if max_date:
            date_filters.append(
                f'FILTER(?transactionDate <= "{max_date.isoformat()}"^^xsd:date)'
            )
        date_filter_str = "\n            ".join(date_filters)

        query = f"""
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ppi: <http://landregistry.data.gov.uk/def/ppi/>
        PREFIX lrcommon: <http://landregistry.data.gov.uk/def/common/>

        SELECT ?item ?address ?pricePaid ?transactionDate ?propertyType ?postcode
               ?paon ?saon ?street ?town
        WHERE {{
            ?item a ppi:TransactionRecord ;
                  ppi:pricePaid ?pricePaid ;
                  ppi:transactionDate ?transactionDate ;
                  ppi:propertyAddress ?address ;
                  ppi:propertyType ?propertyType ;
                  ppi:transactionCategory <http://landregistry.data.gov.uk/def/ppi/standardPricePaidTransaction> .

            ?address lrcommon:postcode ?postcode .

            OPTIONAL {{ ?address lrcommon:paon ?paon }}
            OPTIONAL {{ ?address lrcommon:saon ?saon }}
            OPTIONAL {{ ?address lrcommon:street ?street }}
            OPTIONAL {{ ?address lrcommon:town ?town }}

            FILTER(STRSTARTS(?postcode, "{postcode_sector}"))
            {type_filter}
            {date_filter_str}
        }}
        ORDER BY DESC(?transactionDate)
        LIMIT {limit}
        """

        return query

    def _parse_results(self, results: Dict[str, Any]) -> List[TransactionRecord]:
        """Parse SPARQL JSON results into TransactionRecord objects."""
        transactions = []

        bindings = results.get("results", {}).get("bindings", [])

        for binding in bindings:
            try:
                # Extract property type from URI
                prop_type_uri = binding.get("propertyType", {}).get("value", "")
                property_type = self._uri_to_property_type(prop_type_uri)

                record = TransactionRecord(
                    address_uri=binding.get("address", {}).get("value", ""),
                    price_paid=float(binding.get("pricePaid", {}).get("value", 0)),
                    transaction_date=date.fromisoformat(
                        binding.get("transactionDate", {}).get("value", "1900-01-01")
                    ),
                    property_type=property_type,
                    postcode=binding.get("postcode", {}).get("value", ""),
                    paon=binding.get("paon", {}).get("value"),
                    saon=binding.get("saon", {}).get("value"),
                    street=binding.get("street", {}).get("value"),
                    town=binding.get("town", {}).get("value"),
                )
                transactions.append(record)
            except Exception as e:
                logger.warning(f"Failed to parse transaction record: {e}")
                continue

        return transactions

    def _uri_to_property_type(self, uri: str) -> str:
        """Convert Land Registry property type URI to readable string."""
        for name, type_uri in self.PROPERTY_TYPE_URIS.items():
            if uri == type_uri:
                return name
        return "Unknown"

    @staticmethod
    def extract_postcode_sector(postcode: str) -> str:
        """
        Extract postcode sector from full postcode.

        Example: "SW15 6EJ" -> "SW15 6"

        This provides better geographic precision than district alone
        while maintaining reasonable query performance.
        """
        parts = postcode.strip().upper().split()
        if len(parts) == 2 and len(parts[1]) >= 1:
            return f"{parts[0]} {parts[1][0]}"
        return postcode


class HMLRQueryError(Exception):
    """Exception raised when HMLR SPARQL query fails."""

    pass
