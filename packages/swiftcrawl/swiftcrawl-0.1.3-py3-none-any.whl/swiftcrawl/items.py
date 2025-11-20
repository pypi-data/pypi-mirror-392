"""Scrapy-like Item and Field utilities."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional


Serializer = Callable[[Any], Any]


class Field:
    """Describe an Item attribute with optional defaults and serializer."""

    def __init__(
        self,
        *,
        default: Any = None,
        default_factory: Optional[Callable[[], Any]] = None,
        serializer: Optional[Serializer] = None,
    ) -> None:
        if default is not None and default_factory is not None:
            raise ValueError("Field cannot define both default and default_factory")
        self.default = default
        self.default_factory = default_factory
        self.serializer = serializer


class ItemMeta(type):
    """Collect Field definitions declared on Item subclasses."""

    def __new__(mcls, name, bases, attrs):
        fields: Dict[str, Field] = {}
        for base in bases:
            base_fields = getattr(base, "__fields__", {})
            fields.update(base_fields)

        new_attrs = {}
        for attr_name, value in attrs.items():
            if isinstance(value, Field):
                fields[attr_name] = value
            else:
                new_attrs[attr_name] = value

        new_attrs["__fields__"] = fields
        return super().__new__(mcls, name, bases, new_attrs)


class Item(metaclass=ItemMeta):
    """Base class for serialized items."""

    __fields__: Dict[str, Field]

    def __init__(self, **values: Any) -> None:
        object.__setattr__(self, "_data", {})
        for field_name, field in self.__fields__.items():
            if field_name in values:
                value = values.pop(field_name)
            elif field.default_factory is not None:
                value = field.default_factory()
            else:
                value = field.default
            self._data[field_name] = value

        # Allow free-form attributes for flexibility
        for extra_key, extra_value in values.items():
            self._data[extra_key] = extra_value

    def __getattr__(self, item: str) -> Any:
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError(item) from None

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "_data":
            object.__setattr__(self, key, value)
        else:
            self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in self._data.items():
            field = self.__fields__.get(key)
            if field and field.serializer and value is not None:
                result[key] = field.serializer(value)
            else:
                result[key] = value
        return result

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        fields = ", ".join(f"{k}={v!r}" for k, v in self._data.items())
        return f"<{self.__class__.__name__} {fields}>"


__all__ = ["Item", "Field"]
