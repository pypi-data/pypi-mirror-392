"""Async browser client using Camoufox for anti-detection."""

import json as json_lib
import logging
from typing import Any, Dict, Optional
from camoufox.async_api import AsyncCamoufox
from .response import Response

logger = logging.getLogger(__name__)


class AsyncBrowserClient:
    """Async browser client using Camoufox with page.evaluate() for requests."""

    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[Dict[str, str]] = None,
        block_images: bool = True,
        humanize: Optional[float] = None,
        initial_url: Optional[str] = None,
        locale: str = "en-US",
        os: Optional[list] = None,
        geoip: bool = False,
        **kwargs,
    ):
        self.headless = headless
        self.proxy = proxy
        self.block_images = block_images
        self.humanize = humanize
        self.initial_url = initial_url
        self.locale = locale
        self.os = os or ["windows", "macos"]
        self.geoip = geoip
        self.extra_kwargs = kwargs
        self.browser: Optional[AsyncCamoufox] = None
        self.page = None
        self._initialized = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Initialize the browser and page."""
        if not self._initialized:
            logger.info("Launching Camoufox browser...")

            # Prepare browser launch options
            launch_options = {
                "headless": self.headless,
                "locale": self.locale,
                "os": self.os,
                "block_images": self.block_images,
            }

            if self.block_images:
                launch_options["i_know_what_im_doing"] = True

            if self.proxy:
                launch_options["proxy"] = self.proxy

            if self.humanize is not None:
                launch_options["humanize"] = self.humanize

            if self.geoip:
                launch_options["geoip"] = self.geoip

            launch_options.update(self.extra_kwargs)

            # Launch browser
            self.browser = await AsyncCamoufox(**launch_options).__aenter__()
            self.page = await self.browser.new_page()

            logger.info("Camoufox browser ready")

            # Navigate to initial URL if provided (for session/cookie setup)
            if self.initial_url:
                logger.info(f"Navigating to initial URL: {self.initial_url}")
                await self.page.goto(self.initial_url, wait_until="networkidle")

            self._initialized = True

    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            self._initialized = False

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Response:
        """
        Perform GET request using fetch() API (no page navigation).

        This uses the browser context to send a GET request via JavaScript fetch(),
        which is faster than full page navigation and provides access to HTTP metadata.

        IMPORTANT: Requires a valid page context. Either:
        - Set initial_url parameter when creating EasyScraper, OR
        - Call .goto() once before using .get()

        Args:
            url: Target URL
            headers: Custom headers (completely replaces browser defaults)
            additional_headers: Additional headers to merge with browser defaults
            params: Query parameters to append to URL
            **kwargs: Additional fetch options

        Returns:
            Response object with proper HTTP status and headers

        Raises:
            playwright._impl._errors.Error: If no valid page context exists
        """
        if not self._initialized:
            await self.start()

        # Build URL with query parameters
        if params:
            from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            query_params.update(params)
            query_string = urlencode(query_params, doseq=True)
            url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    query_string,
                    parsed.fragment,
                )
            )

        # Determine headers to use
        fetch_headers = {}
        if headers is not None:
            # Complete replacement
            fetch_headers = headers
        elif additional_headers is not None:
            # Merge: get browser defaults first via evaluate, then merge
            browser_headers = await self.page.evaluate(
                """() => {
                return Object.fromEntries(
                    Array.from(document.querySelectorAll('meta[http-equiv]'))
                        .map(meta => [meta.httpEquiv, meta.content])
                );
            }"""
            )
            fetch_headers = {**browser_headers, **additional_headers}

        # Build fetch options
        fetch_options = {
            "method": "GET",
            "headers": fetch_headers,
        }

        # Merge additional fetch options
        fetch_options.update(kwargs)

        # Execute fetch via page.evaluate()
        result = await self.page.evaluate(
            """async (fetchArgs) => {
            const response = await fetch(fetchArgs.url, fetchArgs.options);
            const text = await response.text();
            const headers = {};
            response.headers.forEach((value, key) => {
                headers[key] = value;
            });

            return {
                text: text,
                status: response.status,
                statusText: response.statusText,
                headers: headers,
                url: response.url
            };
        }""",
            {"url": url, "options": fetch_options},
        )

        # Get current cookies
        cookies_list = await self.page.context.cookies()
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies_list}

        return Response(
            text=result["text"],
            status_code=result["status"],
            headers=result["headers"],
            cookies=cookies,
            url=result["url"],
        )

    async def goto(
        self,
        url: str,
        wait_until: Optional[str] = "networkidle",
        wait_for_selector: Optional[str] = None,
        wait_for_timeout: Optional[int] = None,
        **kwargs,
    ) -> Response:
        """
        Navigate to URL using full browser navigation (for JavaScript-rendered content).

        Args:
            url: Target URL
            wait_until: When to consider navigation complete:
                       'load', 'domcontentloaded', 'networkidle', 'commit'
            wait_for_selector: Optional CSS selector to wait for after navigation
            wait_for_timeout: Timeout in milliseconds for selector wait (default: 30000)
            **kwargs: Additional Playwright goto() options

        Returns:
            Response object with rendered page content
        """
        if not self._initialized:
            await self.start()

        # Navigate to the URL
        await self.page.goto(url, wait_until=wait_until, **kwargs)

        # Wait for specific selector if provided
        if wait_for_selector:
            timeout = wait_for_timeout if wait_for_timeout is not None else 30000
            await self.page.wait_for_selector(wait_for_selector, timeout=timeout)

        # Extract page content and metadata using page.evaluate()
        result = await self.page.evaluate(
            """() => {
            return {
                html: document.documentElement.outerHTML,
                url: window.location.href,
                title: document.title
            };
        }"""
        )

        # Get cookies
        cookies_list = await self.page.context.cookies()
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies_list}

        return Response(
            text=result["html"],
            status_code=200,  # Browser navigation doesn't expose HTTP status easily
            headers={},  # Headers not directly accessible in browser context
            cookies=cookies,
            url=result["url"],
        )

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """
        Perform POST request using page.evaluate() with fetch().

        This uses the browser context to send a POST request via JavaScript fetch(),
        which is faster than full page navigation and maintains browser fingerprint.

        Args:
            url: Target URL
            data: Data to send in POST body (will be JSON encoded)
            headers: Optional custom headers
            **kwargs: Additional fetch options

        Returns:
            Response object
        """
        if not self._initialized:
            await self.start()

        # Prepare headers
        fetch_headers = headers or {}

        # Default to JSON content type if data is provided
        if data and "Content-Type" not in fetch_headers:
            fetch_headers["Content-Type"] = "application/json"

        # Build fetch options
        fetch_options = {
            "method": "POST",
            "headers": fetch_headers,
        }

        if data:
            fetch_options["body"] = json_lib.dumps(data)

        # Merge additional fetch options
        fetch_options.update(kwargs)

        # Execute fetch via page.evaluate()
        result = await self.page.evaluate(
            """async (fetchArgs) => {
            const response = await fetch(fetchArgs.url, fetchArgs.options);
            const text = await response.text();
            const headers = {};
            response.headers.forEach((value, key) => {
                headers[key] = value;
            });

            return {
                text: text,
                status: response.status,
                statusText: response.statusText,
                headers: headers,
                url: response.url
            };
        }""",
            {"url": url, "options": fetch_options},
        )

        # Get current cookies
        cookies_list = await self.page.context.cookies()
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies_list}

        return Response(
            text=result["text"],
            status_code=result["status"],
            headers=result["headers"],
            cookies=cookies,
            url=result["url"],
        )
