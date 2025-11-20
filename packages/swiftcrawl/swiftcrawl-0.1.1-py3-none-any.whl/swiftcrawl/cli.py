"""Command line interface for SwiftCrawl crawler."""

from __future__ import annotations

import argparse
import asyncio
import json
import importlib
import inspect
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Optional, Type
import textwrap

from .crawler import Crawler
from .settings import Settings
from .spider import Spider

logger = logging.getLogger(__name__)


def load_settings() -> Settings:
    """Load settings.py if present, otherwise return defaults."""

    settings_path = Path.cwd() / "settings.py"
    if settings_path.exists():
        try:
            module = importlib.import_module("settings")
            data = getattr(module, "SETTINGS", None)
            if isinstance(data, dict):
                return Settings(data)
        except ModuleNotFoundError as e:
            print(f"Error: Could not import settings module: {e}")
            print("\nMake sure you're running from a SwiftCrawl project directory.")
            print("If you haven't created a project yet, run:")
            print("  swiftcrawl init <project_name>")
            print("  cd <project_name>")
            print("  swiftcrawl crawl <spider_name>")
            sys.exit(1)
    return Settings()


def load_spider(spider_name: str, settings: Optional[Settings] = None) -> Type[Spider]:
    """Load spider class by its name attribute from spiders directory."""

    settings = settings or Settings()
    module_name = settings.get("SPIDERS_MODULE") or "spiders"
    spiders_path = Path.cwd() / module_name
    project_root = Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if not spiders_path.exists():
        print(f"Error: Spiders directory '{module_name}/' not found in current directory.")
        print(f"\nCurrent directory: {Path.cwd()}")
        print("\nMake sure you're running from a SwiftCrawl project directory.")
        print("If you haven't created a project yet, run:")
        print("  swiftcrawl init <project_name>")
        print("  cd <project_name>")
        print("  swiftcrawl crawl <spider_name>")
        sys.exit(1)

    for module_info in pkgutil.iter_modules([str(spiders_path)]):
        module = importlib.import_module(f"{module_name}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not issubclass(obj, Spider) or obj is Spider:
                continue
            candidate_name = getattr(obj, "name", obj.__name__).lower()
            if candidate_name == spider_name.lower():
                return obj

    raise LookupError(f"Spider '{spider_name}' not found in '{module_name}'")


def write_items(items, output_path: str) -> Path:
    """Serialize scraped items to JSON or JSONL file based on extension."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()

    if suffix not in {".json", ".jsonl"}:
        raise ValueError(
            f"Unsupported output format '{suffix}'. Use .json or .jsonl extensions."
        )

    if suffix == ".json":
        logger.info(
            "Writing %s items to %s as JSON array (one line per item)",
            len(items),
            path,
        )
        with path.open("w", encoding="utf-8") as fh:
            fh.write("[\n")
            for idx, item in enumerate(items):
                line = json.dumps(item, ensure_ascii=False)
                if idx < len(items) - 1:
                    fh.write(f"{line},\n")
                else:
                    fh.write(f"{line}\n")
            fh.write("]\n")
    else:
        logger.info("Writing %s items to %s using JSONL format", len(items), path)
        with path.open("w", encoding="utf-8") as fh:
            for item in items:
                fh.write(json.dumps(item, ensure_ascii=False))
                fh.write("\n")

    logger.info("Finished writing items to %s", path)
    return path


def crawl_command(spider_name: str, output: Optional[str] = None) -> None:
    settings = load_settings()
    spider_cls = load_spider(spider_name, settings=settings)
    crawler = Crawler(spider_cls, settings=settings)
    items = asyncio.run(crawler.crawl())
    stats = crawler.get_stats()
    border = "=" * 40
    print(border)
    print(f"Crawl finished | items: {len(items)} | spider: {spider_cls.__name__}")
    print("Statistics:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    print(border)

    if output:
        path = write_items(items, output)
        print(f"Items written to {path}")


def init_command(project_name: str) -> Path:
    """Bootstrap a new SwiftCrawl project."""

    project_root = Path.cwd() / project_name
    if project_root.exists():
        raise FileExistsError(f"Directory '{project_name}' already exists")

    spiders_dir = project_root / "spiders"
    spiders_dir.mkdir(parents=True)
    (spiders_dir / "__init__.py").write_text("", encoding="utf-8")

    sample_spider = (
        textwrap.dedent(
            """
        from swiftcrawl import Request, Spider, Item, Field


        class ExampleItem(Item):
            title = Field()
            author = Field()


        class ExampleSpider(Spider):
            name = "example"
            start_urls = ["https://example.com"]

            async def parse(self, response):
                yield ExampleItem(title=response.soup().title.string)
                yield Request(url="https://example.com/about", callback=self.parse)
        """
        ).strip()
        + "\n"
    )
    (spiders_dir / "example_spider.py").write_text(sample_spider, encoding="utf-8")

    settings_content = (
        textwrap.dedent(
            """
        SETTINGS = {
            "METHOD": "http",
            "MAX_CONCURRENT": 5,
            "REQUESTS_PER_SECOND": None,
            "SPIDERS_MODULE": "spiders",
        }
        """
        ).strip()
        + "\n"
    )
    (project_root / "settings.py").write_text(settings_content, encoding="utf-8")

    border = "=" * 60
    print(border)
    print(f"✓ Initialized SwiftCrawl project at: {project_root}")
    print(border)
    print("\nNext steps:")
    print(f"  1. cd {project_name}")
    print("  2. swiftcrawl crawl example")
    print("\nProject structure:")
    print(f"  {project_name}/")
    print("  ├── spiders/")
    print("  │   ├── __init__.py")
    print("  │   └── example_spider.py")
    print("  └── settings.py")
    print(border)
    return project_root


def configure_logging(verbose: bool) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.WARNING)  # suppress non-SwiftCrawl logs

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    logger = logging.getLogger("swiftcrawl")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()
    logger.propagate = False
    logger.addHandler(handler)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(prog="swiftcrawl", description="SwiftCrawl CLI")
    subparsers = parser.add_subparsers(dest="command")

    crawl_parser = subparsers.add_parser("crawl", help="Run a spider")
    crawl_parser.add_argument("spider", help="Spider name (class name or Spider.name)")
    crawl_parser.add_argument(
        "-o",
        "--output",
        help="Write scraped items to file (.json or .jsonl)",
    )
    crawl_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (includes stack traces)",
    )

    init_parser = subparsers.add_parser("init", help="Bootstrap a new project")
    init_parser.add_argument(
        "project_name", help="Name of the project directory to create"
    )

    args = parser.parse_args(argv)
    if args.command == "crawl":
        configure_logging(args.verbose)
        if args.verbose:
            logger.info("Verbose logging enabled")
        crawl_command(args.spider, output=args.output)
    elif args.command == "init":
        init_command(args.project_name)
    else:
        parser.print_help()


__all__ = [
    "main",
    "load_spider",
    "load_settings",
    "crawl_command",
    "write_items",
    "configure_logging",
    "init_command",
]
