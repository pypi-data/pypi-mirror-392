"""Downloader management across HTTP and browser modes."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, Optional, Tuple, Type
from urllib.parse import urlparse

from .browser_client import AsyncBrowserClient
from .http_client import AsyncHTTPClient
from .request import Request
from .response import Response
from .settings import Settings


class DownloaderManager:
    """Selects and manages the correct downloader for each Request."""

    def __init__(
        self,
        spider,
        settings: Settings,
        http_client_cls: Type[AsyncHTTPClient] = AsyncHTTPClient,
        browser_client_cls: Type[AsyncBrowserClient] = AsyncBrowserClient,
    ) -> None:
        self.spider = spider
        self.settings = settings
        self.http_client_cls = http_client_cls
        self.browser_client_cls = browser_client_cls
        self._downloaders: Dict[str, object] = {}
        self._browser_initialized = False

    async def start(self) -> None:
        """Lazy initialization happens per method."""

    async def close(self) -> None:
        for downloader in self._downloaders.values():
            if hasattr(downloader, "close"):
                await downloader.close()
        self._downloaders.clear()
        self._browser_initialized = False

    async def download(self, request: Request) -> Tuple[Response, str]:
        method = self.select_method(request)
        downloader = await self._init_downloader(method)
        if method == "http":
            response = await self._execute_http(downloader, request)
        elif method == "browser":
            response = await self._execute_browser(downloader, request)
        else:
            raise NotImplementedError(f"Method '{method}' is not supported yet")
        return response, method

    def select_method(self, request: Request) -> str:
        url = request.url
        candidates = [
            request.method,
            self._match_url(url, self.spider.url_methods),
            self._match_domain(url, self.spider.domain_methods),
            self._match_url(url, self.settings.get("URL_METHODS")),
            self._match_domain(url, self.settings.get("DOMAIN_METHODS")),
            getattr(self.spider, "method", None),
            self.settings.get("METHOD"),
        ]

        for candidate in candidates:
            if candidate:
                method = candidate.lower()
                if method not in {"http", "browser"}:
                    raise NotImplementedError(
                        f"Downloader method '{method}' is not implemented"
                    )
                return method
        return "http"

    def get_page(self):
        browser = self._downloaders.get("browser")
        if browser and hasattr(browser, "page"):
            return browser.page
        raise AttributeError("Browser page is not available")

    # Internal helpers -------------------------------------------------
    async def _init_downloader(self, method: str):
        if method in self._downloaders:
            return self._downloaders[method]

        if method == "http":
            options = dict(self.settings.get("HTTP_OPTIONS"))
            downloader = self.http_client_cls(**options)
            await downloader.start()
        elif method == "browser":
            options = {
                "headless": self.settings.get("HEADLESS"),
                "block_images": self.settings.get("BLOCK_IMAGES"),
            }
            options.update(dict(self.settings.get("BROWSER_OPTIONS")))
            downloader = self.browser_client_cls(**options)
            await downloader.start()
            self._downloaders[method] = downloader
            if not self._browser_initialized:
                await self.spider.warmup()
                self._browser_initialized = True
            return downloader
        else:
            raise NotImplementedError(f"Unsupported method: {method}")

        self._downloaders[method] = downloader
        return downloader

    async def _execute_http(
        self, client: AsyncHTTPClient, request: Request
    ) -> Response:
        if request.http_method == "GET":
            return await client.get(
                request.url, headers=request.headers, params=request.params
            )
        return await client.post(
            request.url,
            data=request.data,
            json=request.meta.get("json"),
            headers=request.headers,
        )

    async def _execute_browser(
        self, client: AsyncBrowserClient, request: Request
    ) -> Response:
        if request.use_goto:
            return await client.goto(
                request.url,
                wait_for_selector=request.wait_for_selector,
                wait_for_timeout=request.wait_for_timeout,
            )

        if request.http_method == "GET":
            return await client.get(
                request.url,
                headers=request.headers,
                additional_headers=request.additional_headers,
                params=request.params,
            )

        return await client.post(
            request.url,
            data=request.data,
            headers=request.headers,
        )

    def _match_domain(self, url: str, mapping: Dict[str, str]) -> Optional[str]:
        if not mapping:
            return None
        domain = urlparse(url).hostname or ""
        for pattern, method in mapping.items():
            if fnmatch.fnmatch(domain, pattern):
                return method
        return None

    def _match_url(self, url: str, mapping: Dict[str, str]) -> Optional[str]:
        if not mapping:
            return None
        for pattern, method in mapping.items():
            if self._match_pattern(url, pattern):
                return method
        return None

    def _match_pattern(self, url: str, pattern: str) -> bool:
        if pattern.startswith("regex:"):
            regex = pattern.split("regex:", 1)[1]
            return re.search(regex, url) is not None
        return fnmatch.fnmatch(url, pattern)


__all__ = ["DownloaderManager"]
