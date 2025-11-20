"""Request abstractions for the crawler system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
import itertools


CallbackType = Callable[..., Any]

_COUNTER = itertools.count()


@dataclass(order=True)
class Request:
    """Encapsulates the information required to schedule a crawl request."""

    sort_index: tuple[int, int] = field(init=False, repr=False)
    url: str = field(compare=False)
    callback: CallbackType = field(compare=False)
    priority: int = field(default=0, compare=False)
    http_method: str = field(default="GET", compare=False)
    method: Optional[str] = field(default=None, compare=False)
    meta: Dict[str, Any] = field(default_factory=dict, compare=False)
    headers: Optional[Dict[str, str]] = field(default=None, compare=False)
    additional_headers: Optional[Dict[str, str]] = field(default=None, compare=False)
    data: Optional[Dict[str, Any]] = field(default=None, compare=False)
    params: Optional[Dict[str, Any]] = field(default=None, compare=False)
    dont_filter: bool = field(default=False, compare=False)
    errback: Optional[CallbackType] = field(default=None, compare=False)
    use_goto: bool = field(default=False, compare=False)
    wait_for_selector: Optional[str] = field(default=None, compare=False)
    wait_for_timeout: Optional[int] = field(default=None, compare=False)

    def __post_init__(self) -> None:
        self.http_method = self.http_method.upper()
        if self.http_method not in {"GET", "POST"}:
            raise ValueError(
                f"Unsupported http_method '{self.http_method}'. Use 'GET' or 'POST'."
            )
        if not callable(self.callback):
            raise TypeError("callback must be callable")
        if self.errback is not None and not callable(self.errback):
            raise TypeError("errback must be callable when provided")

        counter_value = next(_COUNTER)
        self.sort_index = (self.priority, counter_value)

    def fingerprint(self) -> str:
        """Return a deterministic fingerprint for deduplication."""

        parts = [
            self.url,
            self.http_method,
            self.method or "",
            str(self.params or {}),
            str(self.data or {}),
        ]
        return "|".join(parts)


__all__ = ["Request", "CallbackType"]
