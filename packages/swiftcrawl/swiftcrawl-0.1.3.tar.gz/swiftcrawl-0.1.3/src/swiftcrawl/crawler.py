"""Crawler orchestration engine."""

from __future__ import annotations

import asyncio
import collections.abc as cabc
import inspect
import logging
import time
import json
from typing import Any, List, Optional

from .downloader import DownloaderManager
from .request import Request
from .scheduler import Scheduler
from .settings import Settings
from .items import Item

logger = logging.getLogger(__name__)


class Crawler:
    """Coordinates Spider, Scheduler and Downloader to execute a crawl."""

    def __init__(
        self,
        spider_cls,
        settings: Optional[Settings] = None,
        *,
        downloader_cls=DownloaderManager,
        scheduler_cls=Scheduler,
        downloader_kwargs: Optional[dict] = None,
    ) -> None:
        base_settings = settings.copy() if settings else Settings()
        merged_settings = base_settings.merge_spider_settings(
            getattr(spider_cls, "custom_settings", None)
        )
        self.settings = merged_settings
        self.spider = spider_cls(settings=self.settings)
        self.spider.set_crawler(self)
        downloader_kwargs = downloader_kwargs or {}
        self.downloader = downloader_cls(
            self.spider, self.settings, **downloader_kwargs
        )
        self.scheduler = scheduler_cls(self.settings)
        self.items: List[Any] = []
        self.stats = {
            "scheduled": 0,
            "requests": 0,
            "responses": 0,
            "items": 0,
            "errors": 0,
            "retries": 0,
        }

    async def crawl(self) -> List[Any]:
        await self.downloader.start()
        await self.scheduler.start()
        await self._schedule_start_requests()

        worker_total = max(1, int(self.settings.get("MAX_CONCURRENT") or 1))
        workers = [asyncio.create_task(self._worker(i)) for i in range(worker_total)]
        await asyncio.gather(*workers)
        await self.spider.closed()
        await self.downloader.close()
        return self.items

    # ------------------------------------------------------------------
    async def _schedule_start_requests(self) -> None:
        await self._consume_start_iterable(self.spider.start_requests())

    async def _consume_start_iterable(self, iterable) -> None:
        if inspect.isasyncgen(iterable):
            async for request in iterable:
                await self._schedule_request(request)
            return

        if inspect.isawaitable(iterable):
            resolved = await iterable
            if resolved is None:
                return
            await self._consume_start_iterable(resolved)
            return

        if isinstance(iterable, cabc.Iterable):
            for request in iterable:
                await self._schedule_request(request)

    async def _worker(self, worker_id: int) -> None:
        while True:
            request = await self.scheduler.next_request()
            if request is None:
                break

            self.stats["requests"] += 1
            start_time = time.monotonic()
            status_code: Optional[int] = None
            try:
                response, method = await self.downloader.download(request)
                status_code = getattr(response, "status_code", None)
                response.meta = request.meta
                response.request = request
                self.stats["responses"] += 1
                self.spider._set_active_method(method)
                await self._process_output(request.callback(response))
                elapsed = time.monotonic() - start_time
                logger.info(
                    "Processed %s %s | status=%s | %.2fms",
                    request.http_method,
                    request.url,
                    status_code,
                    elapsed * 1000,
                )
            except Exception as exc:
                self.stats["errors"] += 1
                message = (
                    f"Request error for {request.http_method} {request.url}: {exc}"
                )
                if logger.isEnabledFor(logging.DEBUG):
                    logger.exception(message)
                else:
                    logger.error("%s (re-run with -v for stack trace)", message)
                await self._handle_error(request, exc)
            finally:
                await self.scheduler.record_result(request, start_time, status_code)
                self.scheduler.request_finished(request)
                self.spider._set_active_method(None)

    async def _handle_error(self, request: Request, error: Exception) -> None:
        if request.errback:
            await self._process_output(request.errback(error))

        retries_enabled = self.settings.get("RETRY_ENABLED")
        max_retries = int(self.settings.get("RETRY_TIMES") or 0)
        attempts = int(request.meta.get("_retries", 0))
        if retries_enabled and attempts < max_retries:
            request.meta["_retries"] = attempts + 1
            request.dont_filter = True
            self.stats["retries"] += 1
            await self.scheduler.enqueue(request)

    async def _process_output(self, output) -> None:
        if output is None:
            return

        if inspect.isawaitable(output) and not inspect.isasyncgen(output):
            resolved = await output
            await self._process_output(resolved)
            return

        if inspect.isasyncgen(output):
            async for item in output:
                await self._process_output(item)
            return

        if isinstance(output, Request):
            logger.debug("Enqueuing new request: %s", output.url)
            await self._schedule_request(output)
            return

        if isinstance(output, Item):
            output = output.to_dict()

        if isinstance(output, dict):
            self.items.append(output)
            self.stats["items"] += 1
            logger.info("Written: %s", json.dumps(output, ensure_ascii=False))
            return

        if isinstance(output, (list, tuple, set)):
            for item in output:
                await self._process_output(item)
            return

        if isinstance(output, cabc.Iterable) and not isinstance(output, (str, bytes)):
            for item in output:
                await self._process_output(item)
            return

        raise TypeError(f"Unsupported yield type: {type(output)!r}")

    async def _schedule_request(self, request: Request) -> None:
        added = await self.scheduler.enqueue(request)
        if added:
            self.stats["scheduled"] += 1
            logger.debug(
                "Scheduled request #%s: %s", self.stats["scheduled"], request.url
            )

    def get_stats(self) -> dict:
        return dict(self.stats)


__all__ = ["Crawler"]
