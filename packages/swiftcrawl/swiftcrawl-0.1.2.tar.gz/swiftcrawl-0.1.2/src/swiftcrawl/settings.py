"""Settings helper for the crawler stack."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


class Settings(dict):
    """Dictionary-like settings container with sensible defaults."""

    DEFAULTS: Dict[str, Any] = {
        "METHOD": "http",
        "DOMAIN_METHODS": {},
        "URL_METHODS": {},
        "MAX_CONCURRENT": 10,
        "MAX_CONCURRENT_PER_DOMAIN": {},
        "REQUESTS_PER_SECOND": None,
        "DOMAIN_DELAYS": {},
        "AUTO_THROTTLE": False,
        "AUTO_THROTTLE_START": 1.0,
        "AUTO_THROTTLE_MAX": 60.0,
        "AUTO_THROTTLE_TARGET": 1.0,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "HEADLESS": True,
        "BLOCK_IMAGES": True,
        "DEDUPLICATE": True,
        "HTTP_OPTIONS": {},
        "BROWSER_OPTIONS": {},
        "SPIDERS_MODULE": "spiders",
    }

    def __init__(self, values: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__()
        merged = {}
        if values:
            merged.update(values)
        merged.update(kwargs)
        for key, value in merged.items():
            self[key] = value

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        if key in self:
            return super().get(key)
        if key in self.DEFAULTS:
            return self.DEFAULTS[key]
        return default

    @classmethod
    def from_module(cls, module_path: str) -> "Settings":
        """Load settings from a python module containing SETTINGS dict."""

        module = import_module(module_path)
        data: Dict[str, Any] = {}
        if hasattr(module, "SETTINGS"):
            obj = getattr(module, "SETTINGS")
            if isinstance(obj, dict):
                data.update(obj)
        return cls(data)

    @classmethod
    def discover(cls, base_path: Optional[Path] = None) -> "Settings":
        """Load settings.py if it exists next to the working directory."""

        base_path = base_path or Path.cwd()
        settings_path = base_path / "settings.py"
        if settings_path.exists():
            module_path = settings_path.stem
            return cls.from_module(module_path)
        return cls()

    def merge_spider_settings(
        self, spider_settings: Optional[Dict[str, Any]]
    ) -> "Settings":
        merged = Settings(dict(self))
        if not spider_settings:
            return merged
        merged.update(spider_settings)
        return merged

    def as_dict(self) -> Dict[str, Any]:
        data = dict(self.DEFAULTS)
        data.update(self)
        return data

    def copy(self) -> "Settings":  # type: ignore[override]
        return Settings(dict(self))


def load_settings(paths: Optional[Iterable[str]] = None) -> Settings:
    """Helper for CLI to load the first available settings module."""

    if paths is None:
        paths = ["settings"]

    for module_path in paths:
        try:
            return Settings.from_module(module_path)
        except ModuleNotFoundError:
            continue
    return Settings()


__all__ = ["Settings", "load_settings"]
