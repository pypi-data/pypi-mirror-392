from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Any
import cattrs

__all__ = ["get_converter", "new_converter"]

_converter: cattrs.Converter | None = None


def _install_default_hooks(conv: cattrs.Converter) -> None:
    # datetime / date from ISO8601 strings
    conv.register_structure_hook(
        datetime,
        lambda v, _: datetime.fromisoformat(v) if isinstance(v, str) else v,
    )
    conv.register_structure_hook(
        date,
        lambda v, _: date.fromisoformat(v) if isinstance(v, str) else v,
    )

    # Generic Enum support: accept actual Enum, value, or name
    def _enum_hook(t: type[Enum]):
        def _struct(v: Any, _t: Any) -> Enum:
            if isinstance(v, t):
                return v
            try:
                return t(v)  # by value
            except Exception:
                return t[str(v)]  # by name

        return _struct

    conv.register_structure_hook_factory(
        lambda t: isinstance(t, type) and issubclass(t, Enum),
        lambda t: _enum_hook(t),
    )

    # Add more hooks here (e.g., Decimal, UUID, your UrlRef/SortOrder VOs, etc.)


def new_converter() -> cattrs.Converter:
    """Build a fresh, fully-configured converter (handy for tests)."""
    conv = cattrs.Converter()
    _install_default_hooks(conv)
    return conv


def get_converter() -> cattrs.Converter:
    """Global, lazily-initialized converter for app runtime."""
    global _converter
    if _converter is None:
        _converter = new_converter()
    return _converter
