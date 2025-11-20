"""Tests for the HTML conversion helpers and converters."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from extract2md._html import to_markdown
from extract2md.converters.readability import ReadabilityConverter, _ensure_node_path
from extract2md.models import Extract2MarkdownConverterError


def test_to_markdown_delegates_to_named_converter(monkeypatch):
    """Passing a converter name should be respected."""

    class FakeConverter:
        name = "fake"
        description = "fake converter"

        def __init__(self) -> None:
            self.html = None

        def convert(self, html: str) -> str:
            self.html = html
            return "Body"

    fake = FakeConverter()

    def fake_get(name=None):  # noqa: ANN001
        assert name == "fake"
        return fake

    monkeypatch.setattr("extract2md._html.get_converter", fake_get)

    html = "<html><body><p>Body</p></body></html>"
    result = to_markdown(html, converter="fake")

    assert result == "Body"
    assert fake.html == html


def test_to_markdown_unknown_converter_raises() -> None:
    """Unknown converter names should raise converter errors."""
    html = "<html><body>content</body></html>"
    with pytest.raises(Extract2MarkdownConverterError):
        to_markdown(html, converter="doesnotexist")


def test_readability_converter_uses_readability_and_markdownify(monkeypatch):
    """Successful conversion should invoke both readabilipy and markdownify."""
    recorded = {}

    def fake_simple_json_from_html_string(html, use_readability):  # noqa: ANN001
        recorded["html"] = html
        recorded["use_readability"] = use_readability
        return {"content": "<p>Body</p>"}

    def fake_markdownify(value, heading_style=None):  # noqa: ANN001
        recorded["markdown_input"] = value
        recorded["heading_style"] = heading_style
        return "Body"

    monkeypatch.setattr(
        "extract2md.converters.readability.readabilipy.simple_json.simple_json_from_html_string",
        fake_simple_json_from_html_string,
    )
    monkeypatch.setattr(
        "extract2md.converters.readability.markdownify.markdownify",
        fake_markdownify,
    )

    converter = ReadabilityConverter()
    result = converter.convert("<html><body><p>Body</p></body></html>")

    assert result == "Body"
    assert recorded["html"] == "<html><body><p>Body</p></body></html>"
    assert recorded["use_readability"] is True
    assert recorded["markdown_input"] == "<p>Body</p>"


def test_readability_converter_handles_empty_payload(monkeypatch):
    """Empty Readability content should raise a clear error."""

    def fake_simple_json_from_html_string(*args, **kwargs):  # noqa: ANN001
        return {"content": ""}

    monkeypatch.setattr(
        "extract2md.converters.readability.readabilipy.simple_json.simple_json_from_html_string",
        fake_simple_json_from_html_string,
    )

    converter = ReadabilityConverter()
    with pytest.raises(Extract2MarkdownConverterError):
        converter.convert("<html></html>")


def test_ensure_node_path_inserts_directory(monkeypatch, tmp_path: Path):
    """EXTRACT2MD_NODE_PATH should be prepended to PATH when valid."""
    node_dir = tmp_path / "node"
    node_dir.mkdir()

    monkeypatch.setenv("EXTRACT2MD_NODE_PATH", str(node_dir))
    monkeypatch.setenv("PATH", "/usr/bin")

    _ensure_node_path()

    assert str(node_dir) == os.environ["PATH"].split(":")[0]


def test_ensure_node_path_ignores_missing_entries(monkeypatch, tmp_path: Path):
    """Non-existent paths should not be added to PATH."""
    monkeypatch.setenv("EXTRACT2MD_NODE_PATH", str(tmp_path / "missing"))
    existing_path = "/usr/bin"
    monkeypatch.setenv("PATH", existing_path)

    _ensure_node_path()

    assert os.environ["PATH"] == existing_path
