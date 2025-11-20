"""HTML conversion helpers for extract2md."""

from __future__ import annotations

from typing import Any, Optional

from extract2md.converters import get_converter
from extract2md.models import (
    Extract2MarkdownContentTypeError,
    Extract2MarkdownToMarkdownError,
)

HTML_TAG_THRESHOLD = 100


def to_markdown(
        html: str,
        content_type: Optional[Any] = None,
        *,
        converter: str | None = None,
) -> str:
    """Convert raw HTML into Markdown."""

    content_type_value = str(content_type or "")
    is_content_type_html = (
            not content_type_value or "text/html" in content_type_value.lower()
    )
    if not is_content_type_html:
        raise Extract2MarkdownContentTypeError(
            f"Received non-html content type {content_type}. Here is the raw content:\n{html}"
        )

    is_page_html = "<html" in html[:HTML_TAG_THRESHOLD].lower()
    if not is_page_html:
        raise Extract2MarkdownToMarkdownError(
            "Not a valid HTML document. "
            f"Here are the first {HTML_TAG_THRESHOLD} characters:\n"
            f"{html[:HTML_TAG_THRESHOLD]}"
        )

    converter_impl = get_converter(converter)
    return converter_impl.convert(html)
