"""Base Spider implementation inspired by Scrapy's API."""

from __future__ import annotations

from typing import AsyncIterator, Dict, List, Optional

from .request import Request
from .settings import Settings


class Spider:
    """Base class that users inherit to describe crawl logic."""

    name: Optional[str] = None
    start_urls: List[str] = []

    method: str = "http"
    domain_methods: Dict[str, str] = {}
    url_methods: Dict[str, str] = {}
    custom_settings: Dict[str, str] = {}

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or Settings()
        self._crawler = None
        self._active_method: Optional[str] = None

    # Lifecycle -----------------------------------------------------------
    def set_crawler(self, crawler: "Crawler") -> None:  # pragma: no cover - circular
        self._crawler = crawler

    @property
    def crawler(self) -> "Crawler":  # pragma: no cover - set in runtime
        if self._crawler is None:
            raise RuntimeError("Spider is not attached to a crawler yet")
        return self._crawler

    async def warmup(self) -> None:
        """Hook executed after the downloader starts (browser only)."""

    async def closed(self) -> None:
        """Hook executed once the crawl is finished."""

    async def start_requests(self) -> AsyncIterator[Request]:
        """Yield Request objects derived from start_urls by default."""

        for url in self.start_urls:
            yield Request(url=url, callback=self.parse, method=self.method)

    async def parse(self, response):  # pragma: no cover - to be overridden
        raise NotImplementedError("Spiders must implement the parse() callback")

    # Helpers -------------------------------------------------------------
    @property
    def client_type(self) -> Optional[str]:
        return self._active_method

    @property
    def page(self):  # pragma: no cover - delegated to downloader
        if self._crawler is None:
            raise AttributeError("Spider has no crawler yet")
        return self._crawler.downloader.get_page()

    def _set_active_method(self, method: Optional[str]) -> None:
        self._active_method = method


__all__ = ["Spider"]
