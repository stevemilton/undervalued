"""Address Matcher for UPRN resolution.

Matches property addresses to their Unique Property Reference Numbers (UPRNs)
using fuzzy matching and address parsing.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class AddressComponents:
    """Parsed address components following BS7666 standard."""

    paon: Optional[str] = None  # Primary Addressable Object Name (building number/name)
    saon: Optional[str] = None  # Secondary Addressable Object Name (flat/unit)
    street: Optional[str] = None
    locality: Optional[str] = None
    town: Optional[str] = None
    postcode: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSONB storage."""
        return {
            "paon": self.paon,
            "saon": self.saon,
            "street": self.street,
            "town": self.town,
            "postcode": self.postcode,
        }


class AddressMatcher:
    """
    Matches and parses UK property addresses.

    This service handles:
    - Parsing raw address strings into BS7666 components
    - Fuzzy matching between listing addresses and Land Registry data
    - Postcode normalization and sector extraction

    Note: Full UPRN resolution typically requires the OS AddressBase product
    which is licensed. This implementation provides best-effort matching.

    Example:
        >>> matcher = AddressMatcher()
        >>> components = matcher.parse_address("Flat 2, 45 High Street, London, SW15 6EJ")
        >>> similarity = matcher.compare_addresses(addr1, addr2)
    """

    # Common street type abbreviations
    STREET_TYPES = {
        "ROAD": "RD",
        "STREET": "ST",
        "AVENUE": "AVE",
        "LANE": "LN",
        "DRIVE": "DR",
        "CLOSE": "CL",
        "WAY": "WY",
        "PLACE": "PL",
        "COURT": "CT",
        "GARDENS": "GDNS",
        "GROVE": "GR",
        "TERRACE": "TER",
        "CRESCENT": "CRES",
        "PARK": "PK",
        "SQUARE": "SQ",
    }

    # UK postcode regex pattern
    POSTCODE_PATTERN = re.compile(
        r"([A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2})",
        re.IGNORECASE,
    )

    # Flat/unit patterns
    FLAT_PATTERN = re.compile(
        r"(?:flat|apt|apartment|unit)\s*(\d+[a-z]?)",
        re.IGNORECASE,
    )

    # House number pattern
    HOUSE_NUMBER_PATTERN = re.compile(
        r"^(\d+[a-z]?(?:-\d+[a-z]?)?)\s*,?\s*(.+)",
        re.IGNORECASE,
    )

    def parse_address(self, raw_address: str) -> AddressComponents:
        """
        Parse a raw address string into BS7666 components.

        Args:
            raw_address: Full address string

        Returns:
            AddressComponents with extracted fields
        """
        if not raw_address:
            return AddressComponents()

        address = raw_address.strip().upper()
        components = AddressComponents()

        # Extract postcode first (most reliable)
        postcode_match = self.POSTCODE_PATTERN.search(address)
        if postcode_match:
            components.postcode = self._normalize_postcode(postcode_match.group(1))
            address = address[: postcode_match.start()].strip()

        # Split remaining address into parts
        parts = [p.strip() for p in address.split(",") if p.strip()]

        if not parts:
            return components

        # Extract flat/unit number (SAON)
        flat_match = self.FLAT_PATTERN.search(parts[0])
        if flat_match:
            components.saon = f"FLAT {flat_match.group(1).upper()}"
            # Remove flat from first part
            parts[0] = self.FLAT_PATTERN.sub("", parts[0]).strip()

        # Extract house number (PAON)
        if parts:
            house_match = self.HOUSE_NUMBER_PATTERN.match(parts[0])
            if house_match:
                components.paon = house_match.group(1).upper()
                components.street = house_match.group(2).strip()
            else:
                # First part might just be building name
                if len(parts) > 1:
                    components.paon = parts[0]
                    components.street = parts[1] if len(parts) > 1 else None
                else:
                    components.street = parts[0]

        # Town is typically the last part before postcode
        if len(parts) > 2:
            components.town = parts[-1] if len(parts) >= 2 else None

        return components

    def compare_addresses(
        self,
        addr1: AddressComponents,
        addr2: AddressComponents,
    ) -> float:
        """
        Calculate similarity score between two addresses.

        Returns a score from 0.0 (no match) to 1.0 (exact match).

        Args:
            addr1: First address
            addr2: Second address

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not addr1 or not addr2:
            return 0.0

        score = 0.0
        weights = {
            "postcode": 0.35,
            "paon": 0.25,
            "street": 0.25,
            "saon": 0.10,
            "town": 0.05,
        }

        # Postcode match (most important)
        if addr1.postcode and addr2.postcode:
            if addr1.postcode == addr2.postcode:
                score += weights["postcode"]
            elif self._postcodes_same_sector(addr1.postcode, addr2.postcode):
                score += weights["postcode"] * 0.5

        # PAON (house number) match
        if addr1.paon and addr2.paon:
            if self._normalize_paon(addr1.paon) == self._normalize_paon(addr2.paon):
                score += weights["paon"]

        # Street match (with normalization)
        if addr1.street and addr2.street:
            street_sim = self._street_similarity(addr1.street, addr2.street)
            score += weights["street"] * street_sim

        # SAON (flat number) match
        if addr1.saon and addr2.saon:
            if self._normalize_saon(addr1.saon) == self._normalize_saon(addr2.saon):
                score += weights["saon"]
        elif not addr1.saon and not addr2.saon:
            score += weights["saon"]  # Both no flat number

        # Town match
        if addr1.town and addr2.town:
            if self._normalize_town(addr1.town) == self._normalize_town(addr2.town):
                score += weights["town"]

        return min(score, 1.0)

    def find_best_match(
        self,
        target: AddressComponents,
        candidates: List[AddressComponents],
        threshold: float = 0.7,
    ) -> Optional[Tuple[AddressComponents, float]]:
        """
        Find the best matching address from a list of candidates.

        Args:
            target: Address to match
            candidates: List of potential matches
            threshold: Minimum similarity score to consider a match

        Returns:
            Tuple of (best match, score) or None if no match above threshold
        """
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            score = self.compare_addresses(target, candidate)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate

        return (best_match, best_score) if best_match else None

    def _normalize_postcode(self, postcode: str) -> str:
        """Normalize postcode format with space."""
        pc = postcode.upper().replace(" ", "")
        if len(pc) >= 5:
            return f"{pc[:-3]} {pc[-3:]}"
        return pc

    def _postcodes_same_sector(self, pc1: str, pc2: str) -> bool:
        """Check if two postcodes are in the same sector."""
        sector1 = self.extract_postcode_sector(pc1)
        sector2 = self.extract_postcode_sector(pc2)
        return sector1 == sector2

    @staticmethod
    def extract_postcode_sector(postcode: str) -> str:
        """Extract postcode sector (e.g., 'SW15 6' from 'SW15 6EJ')."""
        parts = postcode.strip().upper().split()
        if len(parts) == 2 and len(parts[1]) >= 1:
            return f"{parts[0]} {parts[1][0]}"
        return postcode

    def _normalize_paon(self, paon: str) -> str:
        """Normalize PAON (house number)."""
        return paon.upper().replace(" ", "")

    def _normalize_saon(self, saon: str) -> str:
        """Normalize SAON (flat number)."""
        return re.sub(r"\s+", "", saon.upper())

    def _normalize_town(self, town: str) -> str:
        """Normalize town name."""
        return town.upper().strip()

    def _street_similarity(self, street1: str, street2: str) -> float:
        """Calculate similarity between two street names."""
        s1 = self._normalize_street(street1)
        s2 = self._normalize_street(street2)

        if s1 == s2:
            return 1.0

        # Calculate Jaccard similarity
        words1 = set(s1.split())
        words2 = set(s2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _normalize_street(self, street: str) -> str:
        """Normalize street name for comparison."""
        normalized = street.upper().strip()

        # Replace abbreviations with full form
        for full, abbr in self.STREET_TYPES.items():
            normalized = re.sub(rf"\b{abbr}\b", full, normalized)

        # Remove common noise words
        noise_words = ["THE", "AND", "&"]
        for word in noise_words:
            normalized = re.sub(rf"\b{word}\b", "", normalized)

        return " ".join(normalized.split())
