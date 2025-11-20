from __future__ import annotations


class Extract2MarkdownError(RuntimeError):
    """Base class for errors in this package."""


class Extract2MarkdownContentTypeError(Extract2MarkdownError):
    """Raised when HTML cannot be converted to Markdown."""


class Extract2MarkdownToMarkdownError(Extract2MarkdownError):
    """Raised when HTML cannot be converted to Markdown."""


class Extract2MarkdownFetchError(Extract2MarkdownError):
    """Raised when a URL cannot be fetched."""


class Extract2MarkdownConverterError(Extract2MarkdownError):
    """Raised when an HTML conversion backend fails."""
