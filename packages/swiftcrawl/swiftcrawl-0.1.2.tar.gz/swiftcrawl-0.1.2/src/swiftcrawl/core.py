"""Main SwiftCrawl session-based API."""

import logging
from typing import Any, Callable, Dict, Literal, Optional
from .http_client import AsyncHTTPClient
from .browser_client import AsyncBrowserClient
from .response import Response

logger = logging.getLogger(__name__)


class SwiftCrawl:
    """
    Main scraper class with session-based API.

    Usage:
        async with SwiftCrawl(method='http') as session:
            response = await session.get('https://example.com')
            print(response.text)
    """

    def __init__(
        self,
        method: Literal["http", "browser", "auto"] = "http",
        proxy: Optional[str] = None,
        headless: bool = True,
        block_images: bool = True,
        humanize: Optional[float] = None,
        initial_url: Optional[str] = None,
        locale: str = "en-US",
        os: Optional[list] = None,
        geoip: bool = False,
        timeout: float = 30.0,
        max_concurrent: int = 10,
        warmup: Optional[Callable] = None,
        **kwargs,
    ):
        """
        Initialize SwiftCrawl session.

        Args:
            method: Scraping method - 'http', 'browser', or 'auto' (auto not yet implemented)
            proxy: Proxy server URL (for HTTP) or dict config (for browser)
            headless: Run browser in headless mode (browser only)
            block_images: Block image loading (browser only)
            humanize: Human-like behavior intensity (browser only)
            initial_url: URL to visit first for session/cookie setup (browser only)
            locale: Browser locale (browser only)
            os: List of OS to randomly choose from (browser only)
            geoip: Auto-detect geolocation from proxy (browser only)
            timeout: Request timeout in seconds (HTTP only)
            max_concurrent: Max concurrent requests for queue processing
            warmup: Async function to run after browser initialization (browser/auto only).
                    Receives the page object as argument. Use for login, cookie setup, etc.
            **kwargs: Additional client-specific options
        """
        self.method = method
        self.proxy = proxy
        self.max_concurrent = max_concurrent
        self.warmup = warmup
        self.client = None

        # Validate warmup parameter
        if warmup is not None:
            if method == "http":
                raise ValueError(
                    "warmup parameter is only supported for 'browser' and 'auto' methods. "
                    "HTTP mode does not have a page object to pass to the warmup function."
                )
            if not callable(warmup):
                raise TypeError("warmup must be a callable (async function)")

        # Validate browser-only parameters with HTTP mode
        if method == "http":
            browser_only_params = {
                "headless": headless != True,  # Default is True
                "humanize": humanize is not None,
                "block_images": block_images != True,  # Default is True
                "initial_url": initial_url is not None,
                "locale": locale != "en-US",  # Default is 'en-US'
                "geoip": geoip != False,  # Default is False
            }

            used_browser_params = [
                param for param, is_set in browser_only_params.items() if is_set
            ]

            if used_browser_params:
                import warnings

                warnings.warn(
                    f"Browser-only parameters {used_browser_params} are ignored in HTTP mode. "
                    f"These parameters only apply to 'browser' and 'auto' methods.",
                    UserWarning,
                    stacklevel=2,
                )

        # Validate HTTP-only parameters with browser mode
        if method == "browser":
            if timeout != 30.0:  # Default timeout
                import warnings

                warnings.warn(
                    f"HTTP timeout parameter ({timeout}s) is ignored in browser mode. "
                    f"Browser mode uses Playwright's default timeout settings.",
                    UserWarning,
                    stacklevel=2,
                )

        # Store configuration for client initialization
        self._http_config = {
            "proxy": proxy,
            "timeout": timeout,
        }

        self._browser_config = {
            "headless": headless,
            "proxy": {"server": proxy} if proxy and isinstance(proxy, str) else proxy,
            "block_images": block_images,
            "humanize": humanize,
            "initial_url": initial_url,
            "locale": locale,
            "os": os,
            "geoip": geoip,
        }

        # Merge additional kwargs
        self._http_config.update(
            {k: v for k, v in kwargs.items() if k not in self._browser_config}
        )
        self._browser_config.update(
            {k: v for k, v in kwargs.items() if k not in self._http_config}
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_client()

    async def _initialize_client(self):
        """Initialize the appropriate client based on method."""
        if self.method == "http":
            self.client = AsyncHTTPClient(**self._http_config)
            await self.client.start()
        elif self.method == "browser":
            self.client = AsyncBrowserClient(**self._browser_config)
            await self.client.start()

            # Execute warmup function if provided
            if self.warmup is not None:
                logger.info("Executing warmup function...")
                await self.warmup(self.client.page)
                logger.info("Warmup function completed")

        elif self.method == "auto":
            raise NotImplementedError(
                "Auto method selection is not yet implemented. "
                "Please use 'http' or 'browser' explicitly."
            )
        else:
            raise ValueError(
                f"Invalid method: {self.method}. Use 'http', 'browser', or 'auto'."
            )

    async def _close_client(self):
        """Close the active client."""
        if self.client:
            await self.client.close()
            self.client = None

    @property
    def page(self):
        """
        Get the browser page object for advanced operations (browser mode only).

        Returns:
            Playwright Page object for direct browser manipulation

        Raises:
            AttributeError: If not using browser mode
        """
        if self.method != "browser":
            raise AttributeError(
                f"page property is only available in browser mode. "
                f"Current mode: {self.method}"
            )
        if self.client is None:
            raise AttributeError(
                "Client not initialized. Use 'async with EasyScraper()' context manager."
            )
        return self.client.page

    async def get(self, url: str, **kwargs) -> Response:
        """
        Perform GET request using fetch() API (browser) or HTTP client.

        For browser mode: Uses JavaScript fetch() for fast, lightweight requests.
        Use .goto() instead if you need full page navigation with JavaScript rendering.

        Args:
            url: Target URL
            headers: Custom headers (completely replaces defaults, browser only)
            additional_headers: Headers to merge with defaults (browser only)
            params: Query parameters to append to URL (browser only)
            **kwargs: Additional request parameters (client-specific)

        Returns:
            Response object with .text, .json(), .soup(), .tree(), etc.
        """
        if self.client is None:
            await self._initialize_client()

        # Validate browser-only parameters
        if self.method == "http":
            browser_only_params = ["additional_headers"]
            used_params = [p for p in browser_only_params if p in kwargs]
            if used_params:
                raise ValueError(
                    f"Parameters {used_params} are only supported in browser mode. "
                    f"Current mode: {self.method}"
                )

        return await self.client.get(url, **kwargs)

    async def goto(
        self,
        url: str,
        wait_until: Optional[str] = "networkidle",
        wait_for_selector: Optional[str] = None,
        wait_for_timeout: Optional[int] = None,
        **kwargs,
    ) -> Response:
        """
        Navigate to URL using full browser navigation (browser mode only).

        Use this method when you need JavaScript rendering or full page loads.
        For simple HTTP requests, use .get() which is faster.

        Args:
            url: Target URL
            wait_until: When to consider navigation complete:
                       'load', 'domcontentloaded', 'networkidle', 'commit'
            wait_for_selector: Optional CSS selector to wait for after navigation
            wait_for_timeout: Timeout in milliseconds for selector wait
            **kwargs: Additional Playwright goto() options

        Returns:
            Response object with rendered page content

        Raises:
            AttributeError: If not using browser mode
        """
        if self.method != "browser":
            raise AttributeError(
                f"goto() method is only available in browser mode. "
                f"Current mode: {self.method}. Use .get() instead."
            )

        if self.client is None:
            await self._initialize_client()

        return await self.client.goto(
            url,
            wait_until=wait_until,
            wait_for_selector=wait_for_selector,
            wait_for_timeout=wait_for_timeout,
            **kwargs,
        )

    async def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """
        Perform POST request.

        Args:
            url: Target URL
            data: Form data (HTTP) or dict data (browser via fetch)
            json: JSON data (HTTP only, for browser use data param)
            headers: Optional custom headers
            **kwargs: Additional request parameters (client-specific)

        Returns:
            Response object with .text, .json(), .soup(), .tree(), etc.
        """
        if self.client is None:
            await self._initialize_client()

        if self.method == "http":
            return await self.client.post(
                url, data=data, json=json, headers=headers, **kwargs
            )
        elif self.method == "browser":
            # For browser, use data parameter (will be JSON encoded in fetch)
            post_data = data if data is not None else json
            return await self.client.post(
                url, data=post_data, headers=headers, **kwargs
            )
        else:
            raise ValueError(f"Invalid method: {self.method}")
