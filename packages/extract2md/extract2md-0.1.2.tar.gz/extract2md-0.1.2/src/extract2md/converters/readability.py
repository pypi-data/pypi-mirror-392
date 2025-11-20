"""Readability + markdownify based converter."""

from __future__ import annotations

import os
from pathlib import Path

import markdownify
import readabilipy.simple_json

from extract2md.models import Extract2MarkdownConverterError

from . import HtmlConverter, register_converter


class ReadabilityConverter(HtmlConverter):
    """Use Readabilipy and markdownify to simplify HTML content."""

    name = "readability"
    description = "Readabilipy simple_json + markdownify"

    def convert(self, html: str) -> str:
        _ensure_node_path()
        result = readabilipy.simple_json.simple_json_from_html_string(
            html,
            use_readability=True,
        )
        content = result.get("content") if isinstance(result, dict) else None
        if not content:
            raise Extract2MarkdownConverterError(
                "Readability converter was unable to simplify the document."
            )
        return markdownify.markdownify(
            content,
            heading_style=markdownify.ATX,
        )


def _ensure_node_path() -> None:
    """Ensure the configured Node.js binary directory is on PATH."""
    configured_path = os.environ.get("EXTRACT2MD_NODE_PATH")
    if not configured_path:
        return

    node_path = Path(configured_path).expanduser()
    if not node_path.exists():
        return

    node_dir = node_path if node_path.is_dir() else node_path.parent
    if not node_dir.exists():
        return

    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    dir_str = str(node_dir)
    if dir_str in path_entries:
        return

    filtered_entries = [entry for entry in path_entries if entry]
    os.environ["PATH"] = os.pathsep.join([dir_str, *filtered_entries])


register_converter(ReadabilityConverter())

__all__ = ["ReadabilityConverter"]
