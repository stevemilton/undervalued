"""robots.txt parser for scraping compliance.

Checks if scraping is allowed for a given URL path.
"""

import logging
from typing import Dict, Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class RobotsParser:
    """
    Parser for robots.txt files.

    Used to check if scraping a specific path is allowed
    for our user agent.

    Example:
        >>> parser = RobotsParser()
        >>> allowed = await parser.can_fetch(
        ...     "https://rightmove.co.uk/robots.txt",
        ...     "/property-for-sale"
        ... )
    """

    # Cache for parsed robots.txt files
    _cache: Dict[str, "RobotRules"] = {}

    def __init__(self, user_agent: str = "UndervaluedBot"):
        """
        Initialize the parser.

        Args:
            user_agent: User agent to check rules for
        """
        self.user_agent = user_agent.lower()

    async def can_fetch(
        self,
        robots_url: str,
        path: str,
        timeout: int = 10,
    ) -> bool:
        """
        Check if fetching a path is allowed by robots.txt.

        Args:
            robots_url: URL to robots.txt
            path: Path to check
            timeout: Request timeout

        Returns:
            True if fetching is allowed, False otherwise
        """
        try:
            rules = await self._get_rules(robots_url, timeout)
            return rules.is_allowed(self.user_agent, path)
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            # Be conservative: assume not allowed if we can't check
            return False

    async def _get_rules(
        self,
        robots_url: str,
        timeout: int,
    ) -> "RobotRules":
        """Fetch and parse robots.txt, with caching."""
        if robots_url in self._cache:
            return self._cache[robots_url]

        rules = RobotRules()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(robots_url)

                if response.status_code == 200:
                    rules.parse(response.text)
                elif response.status_code == 404:
                    # No robots.txt = everything allowed
                    logger.debug(f"No robots.txt found at {robots_url}")
                else:
                    logger.warning(
                        f"robots.txt returned status {response.status_code}"
                    )

        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching robots.txt from {robots_url}")
        except Exception as e:
            logger.error(f"Error fetching robots.txt: {e}")

        self._cache[robots_url] = rules
        return rules


class RobotRules:
    """
    Parsed rules from a robots.txt file.

    Supports basic directives:
    - User-agent
    - Disallow
    - Allow
    """

    def __init__(self):
        """Initialize empty rules."""
        self.rules: Dict[str, list] = {"*": []}
        self._current_agents: list = []

    def parse(self, content: str) -> None:
        """
        Parse robots.txt content.

        Args:
            content: Raw robots.txt file content
        """
        self._current_agents = []

        for line in content.splitlines():
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Parse directive
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip().lower()
                value = value.strip()

                if key == "user-agent":
                    agent = value.lower()
                    self._current_agents = [agent]
                    if agent not in self.rules:
                        self.rules[agent] = []

                elif key in ("disallow", "allow"):
                    rule = (key, value)
                    for agent in self._current_agents or ["*"]:
                        if agent not in self.rules:
                            self.rules[agent] = []
                        self.rules[agent].append(rule)

    def is_allowed(self, user_agent: str, path: str) -> bool:
        """
        Check if a path is allowed for a user agent.

        Args:
            user_agent: User agent string
            path: URL path to check

        Returns:
            True if allowed, False if disallowed
        """
        agent = user_agent.lower()

        # Find applicable rules
        if agent in self.rules:
            rules = self.rules[agent]
        elif "*" in self.rules:
            rules = self.rules["*"]
        else:
            return True  # No rules = allowed

        # Check rules in order, most specific match wins
        allowed = True
        best_match_len = 0

        for directive, pattern in rules:
            if self._path_matches(path, pattern):
                if len(pattern) >= best_match_len:
                    best_match_len = len(pattern)
                    allowed = directive == "allow"

        return allowed

    def _path_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches a robots.txt pattern."""
        if not pattern:
            return False

        # Simple prefix matching (basic implementation)
        # Full implementation would handle * and $ wildcards
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        else:
            return path.startswith(pattern)
