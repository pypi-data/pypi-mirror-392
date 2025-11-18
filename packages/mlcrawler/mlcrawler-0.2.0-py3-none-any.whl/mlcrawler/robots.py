"""Robots.txt fetching and evaluation utilities."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from .config import Config


@dataclass
class _RobotsRules:
    """Container for cached robots.txt parser state."""

    parser: Optional[RobotFileParser]
    fetched_at: datetime


class RobotsManager:
    """Fetches and caches robots.txt rules per host."""

    def __init__(self, config: Config, *, cache_ttl_seconds: int = 3600):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, _RobotsRules] = {}
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._lock = asyncio.Lock()
        self._client = httpx.AsyncClient(
            headers={"User-Agent": config.user_agent},
            follow_redirects=True,
            timeout=15.0,
        )

    async def close(self):
        """Close HTTP resources."""
        await self._client.aclose()

    async def is_allowed(self, url: str) -> bool:
        """Check whether a URL is allowed by robots.txt.

        Args:
            url: Absolute URL to evaluate

        Returns:
            True if the URL should be fetched, False if disallowed.
        """
        if not self.config.obey_robots:
            return True

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return True

        host = parsed.netloc.lower()

        rules = await self._get_rules(host, parsed.scheme)
        parser = rules.parser if rules else None

        if parser is None:
            # Treat missing or malformed robots as allow-all
            return True

        user_agent = self.config.user_agent or "mlcrawler/0.1 (+contact-url)"
        allowed = parser.can_fetch(user_agent, url)
        if not allowed:
            self.logger.info("Blocked by robots.txt: %s", url)
        return allowed

    async def _get_rules(self, host: str, scheme: str) -> Optional[_RobotsRules]:
        async with self._lock:
            rules = self._cache.get(host)
            if rules and datetime.now() - rules.fetched_at < self._cache_ttl:
                return rules

            new_rules = await self._fetch_rules(host, scheme)
            if new_rules:
                self._cache[host] = new_rules
            return new_rules

    async def _fetch_rules(self, host: str, scheme: str) -> Optional[_RobotsRules]:
        robots_url = f"{scheme}://{host}/robots.txt"
        try:
            response = await self._client.get(robots_url)
        except httpx.HTTPError as exc:
            self.logger.debug("Failed to fetch robots.txt for %s: %s", host, exc)
            return _RobotsRules(parser=None, fetched_at=datetime.now())

        if response.status_code >= 400:
            self.logger.debug(
                "Robots.txt not available for %s (status %s)",
                host,
                response.status_code,
            )
            return _RobotsRules(parser=None, fetched_at=datetime.now())

        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(response.text.splitlines())
        self.logger.debug(
            "Loaded robots.txt for %s (%d bytes)", host, len(response.text)
        )
        return _RobotsRules(parser=parser, fetched_at=datetime.now())
