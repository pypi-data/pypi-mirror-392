"""Async HTTP client with BrowserForge header generation."""

import httpx
from typing import Any, Dict, Optional
from browserforge.headers import HeaderGenerator
from .response import Response


class AsyncHTTPClient:
    """Async HTTP client using httpx with BrowserForge for stealth headers."""

    def __init__(self, proxy: Optional[str] = None, timeout: float = 30.0, **kwargs):
        self.header_generator = HeaderGenerator()
        self.proxy = proxy
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
        self.extra_kwargs = kwargs

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Initialize the HTTP client."""
        if self.client is None:
            client_kwargs = dict(self.extra_kwargs)
            if self.proxy is not None:
                client_kwargs["proxies"] = self.proxy
            client_kwargs.setdefault("timeout", self.timeout)
            self.client = httpx.AsyncClient(**client_kwargs)
            # Follow redirects by default for parity with httpx<0.28 behavior
            self.client.follow_redirects = True

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    def _generate_headers(self) -> Dict[str, str]:
        """Generate random browser headers using BrowserForge."""
        return self.header_generator.generate()

    async def get(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> Response:
        """
        Perform async GET request.

        Args:
            url: Target URL
            headers: Optional custom headers (will be merged with generated headers)
            **kwargs: Additional httpx request parameters

        Returns:
            Response object
        """
        if self.client is None:
            await self.start()

        # Generate stealth headers
        request_headers = self._generate_headers()

        # Merge with custom headers if provided
        if headers:
            request_headers.update(headers)

        response = await self.client.get(url, headers=request_headers, **kwargs)

        return Response(
            text=response.text,
            status_code=response.status_code,
            headers=dict(response.headers),
            cookies={cookie.name: cookie.value for cookie in response.cookies.jar},
            url=str(response.url),
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
        Perform async POST request.

        Args:
            url: Target URL
            data: Form data to send
            json: JSON data to send
            headers: Optional custom headers (will be merged with generated headers)
            **kwargs: Additional httpx request parameters

        Returns:
            Response object
        """
        if self.client is None:
            await self.start()

        # Generate stealth headers
        request_headers = self._generate_headers()

        # Merge with custom headers if provided
        if headers:
            request_headers.update(headers)

        response = await self.client.post(
            url, data=data, json=json, headers=request_headers, **kwargs
        )

        return Response(
            text=response.text,
            status_code=response.status_code,
            headers=dict(response.headers),
            cookies={cookie.name: cookie.value for cookie in response.cookies.jar},
            url=str(response.url),
        )
