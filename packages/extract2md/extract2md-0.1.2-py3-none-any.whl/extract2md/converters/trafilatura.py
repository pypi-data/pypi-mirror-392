"""Trafilatura based converter."""

from __future__ import annotations

import trafilatura

from extract2md.models import Extract2MarkdownConverterError

from . import HtmlConverter, register_converter


class TrafilaturaConverter(HtmlConverter):
    """Use trafilatura.extract() to convert HTML into Markdown."""

    name = "trafilatura"
    description = "Trafilatura markdown output"

    def convert(self, html: str) -> str:
        result = trafilatura.extract(
            html,
            output_format="markdown",
            include_links=True,
        )
        if not result:
            raise Extract2MarkdownConverterError(
                "Trafilatura converter did not return any content."
            )
        return result


register_converter(TrafilaturaConverter())

__all__ = ["TrafilaturaConverter"]
