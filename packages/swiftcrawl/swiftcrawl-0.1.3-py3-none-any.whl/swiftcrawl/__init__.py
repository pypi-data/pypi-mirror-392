"""SwiftCrawl - Web scraping abstraction layer with HTTP and browser support."""

import asyncio

from .core import SwiftCrawl
from .crawler import Crawler
from .request import Request
from .response import Response
from .settings import Settings
from .spider import Spider
from .items import Item, Field

__version__ = "0.1.2"


async def run_spider_async(spider_cls, settings: Settings | None = None):
    crawler = Crawler(spider_cls, settings=settings)
    return await crawler.crawl()


def run_spider(spider_cls, settings: Settings | None = None):
    """Convenience helper to run a spider synchronously."""

    return asyncio.run(run_spider_async(spider_cls, settings=settings))


__all__ = [
    "SwiftCrawl",
    "Response",
    "Spider",
    "Request",
    "Crawler",
    "Settings",
    "Item",
    "Field",
    "run_spider",
    "run_spider_async",
]
