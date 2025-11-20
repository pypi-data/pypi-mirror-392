"""Converter registry used to simplify HTML documents."""

from __future__ import annotations

import importlib
import pkgutil
from typing import Protocol

from extract2md.models import Extract2MarkdownConverterError

DEFAULT_CONVERTER = "trafilatura"


class HtmlConverter(Protocol):
    """Protocol implemented by HTML conversion strategies."""

    name: str
    description: str

    def convert(self, html: str) -> str:
        """Return Markdown content extracted from ``html``."""


_REGISTRY: dict[str, HtmlConverter] = {}
_DISCOVERED = False


def register_converter(converter: HtmlConverter) -> None:
    """Register an ``HtmlConverter`` implementation."""
    _REGISTRY[converter.name] = converter


def _discover_converters() -> None:
    """Import converter modules to populate the registry."""
    global _DISCOVERED
    if _DISCOVERED:
        return

    _DISCOVERED = True
    package_prefix = __name__ + "."
    for module_info in pkgutil.iter_modules(__path__, package_prefix):
        importlib.import_module(module_info.name)


def _ensure_registry() -> None:
    if not _DISCOVERED:
        _discover_converters()


def get_converter(name: str | None = None) -> HtmlConverter:
    """Return the registered converter matching ``name``."""
    _ensure_registry()
    selected_name = name or DEFAULT_CONVERTER
    try:
        return _REGISTRY[selected_name]
    except KeyError as exc:  # pragma: no cover - simple defensive logic
        available = ", ".join(sorted(_REGISTRY))
        raise Extract2MarkdownConverterError(
            f"Unknown converter '{selected_name}'. Available: {available}"
        ) from exc


def get_converter_names() -> list[str]:
    """Return the known converter names."""
    _ensure_registry()
    return sorted(_REGISTRY.keys())


__all__ = [
    "DEFAULT_CONVERTER",
    "HtmlConverter",
    "get_converter",
    "get_converter_names",
    "register_converter",
]
