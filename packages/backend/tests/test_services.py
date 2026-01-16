"""Tests for external service clients."""

from datetime import date

import pytest

from src.services.address_matcher import AddressComponents, AddressMatcher
from src.services.hmlr_client import HMLRClient


class TestAddressMatcher:
    """Tests for AddressMatcher service."""

    def test_parse_simple_address(self):
        """Test parsing a simple address."""
        matcher = AddressMatcher()
        result = matcher.parse_address("42 High Street, London, SW15 6EJ")

        assert result.paon == "42"
        assert "HIGH" in result.street.upper()
        assert result.postcode == "SW15 6EJ"

    def test_parse_flat_address(self):
        """Test parsing address with flat number."""
        matcher = AddressMatcher()
        result = matcher.parse_address("Flat 5, 100 Kings Road, London, SW3 4AA")

        assert result.saon is not None
        assert "5" in result.saon
        assert result.paon == "100"
        assert result.postcode == "SW3 4AA"

    def test_normalize_postcode(self):
        """Test postcode normalization."""
        matcher = AddressMatcher()

        # Test various formats
        assert matcher._normalize_postcode("SW156EJ") == "SW15 6EJ"
        assert matcher._normalize_postcode("sw15 6ej") == "SW15 6EJ"
        assert matcher._normalize_postcode("SW15  6EJ") == "SW15 6EJ"

    def test_extract_postcode_sector(self):
        """Test postcode sector extraction."""
        assert AddressMatcher.extract_postcode_sector("SW15 6EJ") == "SW15 6"
        assert AddressMatcher.extract_postcode_sector("W1A 1AA") == "W1A 1"

    def test_compare_identical_addresses(self):
        """Test comparing identical addresses returns high score."""
        matcher = AddressMatcher()

        addr1 = AddressComponents(
            paon="42",
            street="HIGH STREET",
            town="LONDON",
            postcode="SW15 6EJ",
        )
        addr2 = AddressComponents(
            paon="42",
            street="HIGH STREET",
            town="LONDON",
            postcode="SW15 6EJ",
        )

        score = matcher.compare_addresses(addr1, addr2)
        assert score >= 0.9

    def test_compare_different_addresses(self):
        """Test comparing different addresses returns low score."""
        matcher = AddressMatcher()

        addr1 = AddressComponents(
            paon="42",
            street="HIGH STREET",
            postcode="SW15 6EJ",
        )
        addr2 = AddressComponents(
            paon="100",
            street="KINGS ROAD",
            postcode="SW3 4AA",
        )

        score = matcher.compare_addresses(addr1, addr2)
        assert score < 0.5


class TestHMLRClient:
    """Tests for HMLRClient."""

    def test_extract_postcode_sector(self):
        """Test postcode sector extraction utility."""
        assert HMLRClient.extract_postcode_sector("SW15 6EJ") == "SW15 6"
        assert HMLRClient.extract_postcode_sector("W1A 1AA") == "W1A 1"
        assert HMLRClient.extract_postcode_sector("EC1A 1BB") == "EC1A 1"

    def test_build_query_basic(self):
        """Test SPARQL query building."""
        client = HMLRClient()
        query = client._build_query(
            postcode_sector="SW15 6",
            property_type=None,
            min_date=None,
            max_date=None,
            limit=100,
        )

        assert "SW15 6" in query
        assert "LIMIT 100" in query
        assert "ppi:TransactionRecord" in query

    def test_build_query_with_filters(self):
        """Test query with property type and date filters."""
        client = HMLRClient()
        query = client._build_query(
            postcode_sector="SW15 6",
            property_type="Terraced",
            min_date=date(2024, 1, 1),
            max_date=date(2024, 12, 31),
            limit=50,
        )

        assert "terraced" in query.lower()
        assert "2024-01-01" in query
        assert "2024-12-31" in query
        assert "LIMIT 50" in query

    def test_property_type_mapping(self):
        """Test property type URI mapping."""
        client = HMLRClient()

        # Known types should map
        assert "detached" in client.PROPERTY_TYPE_URIS["Detached"]
        assert "flat" in client.PROPERTY_TYPE_URIS["Flat"]

        # URI to type conversion
        assert client._uri_to_property_type(
            "http://landregistry.data.gov.uk/def/common/terraced"
        ) == "Terraced"

        # Unknown URI
        assert client._uri_to_property_type("unknown-uri") == "Unknown"


class TestScrapedListing:
    """Tests for scraper data structures."""

    def test_sample_listings(self):
        """Test sample listings generator."""
        from src.scrapers import get_sample_listings

        listings = get_sample_listings("SW15")

        assert len(listings) > 0
        assert all(listing.postcode.startswith("SW15") for listing in listings)
        assert all(listing.asking_price > 0 for listing in listings)
