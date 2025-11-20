"""Response class for unified HTTP and browser responses."""

import json as json_lib
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup
from lxml import html as lxml_html


class Response:
    """Unified response object for both HTTP and browser requests."""

    def __init__(
        self,
        text: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
    ):
        self._text = text
        self._status_code = status_code
        self._headers = headers or {}
        self._cookies = cookies or {}
        self._url = url
        self._soup_cache = None
        self._tree_cache = None

    @property
    def text(self) -> str:
        """Get response text content."""
        return self._text

    @property
    def html(self) -> str:
        """Get HTML content (alias for text)."""
        return self._text

    @property
    def status_code(self) -> int:
        """Get HTTP status code."""
        return self._status_code

    @property
    def headers(self) -> Dict[str, str]:
        """Get response headers."""
        return self._headers

    @property
    def cookies(self) -> Dict[str, str]:
        """Get response cookies."""
        return self._cookies

    @property
    def url(self) -> Optional[str]:
        """Get final URL after redirects."""
        return self._url

    def json(self) -> Any:
        """
        Parse response as JSON.

        Handles browser mode responses where JSON might be wrapped in HTML tags.
        """
        text = self._text.strip()

        # Check if response is HTML-wrapped (common in browser mode)
        # This happens when browser renders JSON responses with minimal HTML structure
        if text.startswith("<") and "<body>" in text.lower():
            # Extract content from body tag using BeautifulSoup
            # Reuse soup cache if available, otherwise create temporary soup
            if self._soup_cache is not None:
                soup = self._soup_cache
            else:
                soup = BeautifulSoup(text, "html.parser")

            body = soup.find("body")
            if body:
                # Get text content from body tag
                text = body.get_text().strip()

        return json_lib.loads(text)

    def soup(self) -> BeautifulSoup:
        """Get BeautifulSoup object with 'html.parser'."""
        if self._soup_cache is None:
            self._soup_cache = BeautifulSoup(self._text, "html.parser")
        return self._soup_cache

    def tree(self):
        """Get lxml tree for XPath usage."""
        if self._tree_cache is None:
            self._tree_cache = lxml_html.fromstring(self._text)
        return self._tree_cache

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"
