"""Priority scheduler with rate limiting and auto-throttle support."""

from __future__ import annotations

import asyncio
import heapq
import hashlib
import time
from collections import defaultdict
from typing import Dict, Optional
from urllib.parse import urlparse

from .request import Request
from .settings import Settings


class Scheduler:
    """Manage crawl ordering, deduplication, and concurrency control."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._queue: list[Request] = []
        self._seen: set[str] = set()
        self._condition = asyncio.Condition()

        max_concurrent = max(1, int(self.settings.get("MAX_CONCURRENT") or 1))
        self._global_semaphore = asyncio.Semaphore(max_concurrent)
        self._domain_semaphores: Dict[str, asyncio.Semaphore] = {}
        self._domain_limits: Dict[str, int] = {
            k: max(1, int(v))
            for k, v in self.settings.get("MAX_CONCURRENT_PER_DOMAIN").items()
        }

        self._domain_for_request: Dict[int, str] = {}
        self._active_tasks = 0
        self._idle_event = asyncio.Event()
        self._idle_event.set()

        self._next_global_time = 0.0
        self._next_domain_time: Dict[str, float] = defaultdict(float)
        self._auto_ready_at: Dict[str, float] = defaultdict(float)
        self._auto_delays: Dict[str, float] = defaultdict(
            lambda: float(self.settings.get("AUTO_THROTTLE_START"))
        )

    async def start(self) -> None:
        """Placeholder for API symmetry."""

    async def enqueue(self, request: Request) -> bool:
        """Push a request into the priority queue if not duplicated."""

        if self.settings.get("DEDUPLICATE") and not request.dont_filter:
            fingerprint = self._fingerprint(request)
            if fingerprint in self._seen:
                return False
            self._seen.add(fingerprint)

        async with self._condition:
            heapq.heappush(self._queue, request)
            self._idle_event.clear()
            self._condition.notify_all()
        return True

    async def next_request(self) -> Optional[Request]:
        """Pop the next request after rate/concurrency checks."""

        async with self._condition:
            while not self._queue:
                if self._active_tasks == 0:
                    self._idle_event.set()
                    return None
                await self._condition.wait()
            request = heapq.heappop(self._queue)

        await self._global_semaphore.acquire()
        domain = self._get_domain(request.url)
        domain_sem = self._get_domain_semaphore(domain)
        if domain_sem is not None:
            await domain_sem.acquire()

        await self._apply_rate_limits(request.url)

        self._domain_for_request[id(request)] = domain
        self._active_tasks += 1
        return request

    async def join(self) -> None:
        """Wait until queue is empty and no tasks are inflight."""

        while True:
            if self._idle_event.is_set():
                return
            await asyncio.sleep(0.05)

    def request_finished(self, request: Request) -> None:
        """Mark a request as finished, releasing semaphores."""

        request_id = id(request)
        domain = self._domain_for_request.pop(request_id, None)
        self._active_tasks = max(0, self._active_tasks - 1)
        self._global_semaphore.release()
        if domain:
            domain_sem = self._domain_semaphores.get(domain)
            if domain_sem is not None:
                domain_sem.release()

        if not self._queue and self._active_tasks == 0:
            self._idle_event.set()
            asyncio.create_task(self._notify_idle())

    async def _notify_idle(self) -> None:
        async with self._condition:
            self._condition.notify_all()

    async def record_result(
        self, request: Request, start_time: float, status_code: Optional[int]
    ) -> None:
        if not self.settings.get("AUTO_THROTTLE"):
            return

        domain = self._get_domain(request.url)
        latency = time.monotonic() - start_time
        target = max(float(self.settings.get("AUTO_THROTTLE_TARGET") or 1.0), 0.1)
        current_delay = self._auto_delays[domain]
        target_delay = latency / target
        new_delay = (current_delay + target_delay) / 2.0
        if status_code is None or status_code >= 400:
            new_delay = max(current_delay, new_delay)

        min_delay = float(self.settings.get("AUTO_THROTTLE_START"))
        max_delay = float(self.settings.get("AUTO_THROTTLE_MAX"))
        bounded = max(min_delay, min(new_delay, max_delay))
        self._auto_delays[domain] = bounded

    async def _apply_rate_limits(self, url: str) -> None:
        waits = []
        now = time.monotonic()

        rps = self.settings.get("REQUESTS_PER_SECOND")
        if rps:
            min_interval = 1.0 / float(rps)
            waits.append(max(0.0, self._next_global_time - now))
            self._next_global_time = max(self._next_global_time, now) + min_interval

        domain = self._get_domain(url)
        domain_delay = self.settings.get("DOMAIN_DELAYS").get(domain)
        if domain_delay:
            waits.append(max(0.0, self._next_domain_time[domain] - now))
            self._next_domain_time[domain] = (
                max(self._next_domain_time[domain], now) + domain_delay
            )

        if self.settings.get("AUTO_THROTTLE"):
            ready_at = self._auto_ready_at[domain]
            waits.append(max(0.0, ready_at - now))
            self._auto_ready_at[domain] = max(ready_at, now) + self._auto_delays[domain]

        delay = max(waits) if waits else 0.0
        if delay > 0:
            await asyncio.sleep(delay)

    def _fingerprint(self, request: Request) -> str:
        raw = request.fingerprint().encode()
        return hashlib.sha256(raw).hexdigest()

    def _get_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.hostname or ""

    def _get_domain_semaphore(self, domain: str) -> Optional[asyncio.Semaphore]:
        if not domain:
            return None
        limit = self._domain_limits.get(domain)
        if limit is None:
            return None
        if domain not in self._domain_semaphores:
            self._domain_semaphores[domain] = asyncio.Semaphore(limit)
        return self._domain_semaphores[domain]


__all__ = ["Scheduler"]
