"""
Unit tests for the conversion pipeline that don't require pdfme to be installed.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from toon_to_pdf.converter import (
    _build_text_style,
    _normalize_position,
    _parse_toon,
    _resolve_page_size,
    _transform_to_pdfme_format,
    generate_from_toon,
)


class _FakePage:
    """Minimal stand-in for pdfme.pdf.PDFPage."""

    def __init__(self, width: float, height: float, margin: float) -> None:
        self.width = width
        self.height = height
        self.margin_right = margin
        self.margin_bottom = margin


class FakePDF:
    """A lightweight PDF stub that mimics the bits we rely on."""

    instances: list["FakePDF"] = []

    def __init__(self, page_size: Any = "letter", margin: float = 0, **_: Any) -> None:
        width, height = self._resolve_page_size(page_size)
        self.default_width = width
        self.default_height = height
        self.margin = float(margin)
        self.pages: list[_FakePage] = []
        self._page = None
        self.text_calls = []
        FakePDF.instances.append(self)

    @staticmethod
    def _resolve_page_size(page_size: Any) -> tuple[float, float]:
        preset = {
            "letter": (612.0, 792.0),
            "legal": (612.0, 1008.0),
            "a4": (595.0, 842.0),
        }
        if isinstance(page_size, str):
            return preset.get(page_size.lower(), preset["letter"])
        if isinstance(page_size, (tuple, list)) and len(page_size) == 2:
            return float(page_size[0]), float(page_size[1])
        return preset["letter"]

    @property
    def page(self) -> _FakePage:
        if self._page is None:
            raise AttributeError("No current page")
        return self._page

    def add_page(self) -> None:
        page = _FakePage(self.default_width, self.default_height, self.margin)
        self.pages.append(page)
        self._page = page

    def _text(self, paragraph: dict, **kwargs: Any) -> None:
        record = {"paragraph": paragraph}
        record.update(kwargs)
        self.text_calls.append(record)

    def output(self, buffer) -> None:
        if not self.pages:
            raise Exception("pdf doesn't have any pages")
        buffer.write(b"%PDF-FAKE%")


class GenerateFromToonTests(TestCase):
    """Exercises the high level conversion workflow."""

    def setUp(self) -> None:
        FakePDF.instances.clear()

    def test_generate_from_toon_places_text(self) -> None:
        toon = """
(
  schemas: [
    (
      content: ( type: "text", text: "Hello Test", fontSize: 16 )
      position: ( x: 40, y: 80 )
    )
  ]
  basePdf: "blank"
)
""".strip()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "hello.pdf"
            with patch("toon_to_pdf.converter._load_pdf_class", return_value=FakePDF):
                generate_from_toon(toon, output)

            self.assertTrue(output.exists())
            self.assertEqual(output.read_bytes(), b"%PDF-FAKE%")
            pdf = FakePDF.instances[-1]
            self.assertEqual(len(pdf.pages), 1)
            self.assertEqual(len(pdf.text_calls), 1)
            paragraph = pdf.text_calls[0]["paragraph"]
            self.assertEqual(paragraph["."], "Hello Test")
            self.assertEqual(paragraph["style"]["s"], 16.0)

    def test_generate_from_toon_adds_page_without_schemas(self) -> None:
        toon = '( basePdf: "letter" )'

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "blank.pdf"
            with patch("toon_to_pdf.converter._load_pdf_class", return_value=FakePDF):
                generate_from_toon(toon, output)

            self.assertTrue(output.exists())
            pdf = FakePDF.instances[-1]
            self.assertEqual(len(pdf.pages), 1)
            self.assertEqual(pdf.text_calls, [])


class HelperFunctionTests(TestCase):
    """Unit tests for lower-level helper utilities."""

    def test_transform_adds_defaults_and_normalizes_schema(self) -> None:
        data = {
            "schemas": [
                {
                    "content": {"type": "text", "text": "Hello"},
                }
            ]
        }

        result = _transform_to_pdfme_format(data)

        self.assertEqual(result["basePdf"], "blank")
        self.assertEqual(len(result["schemas"]), 1)
        self.assertEqual(result["schemas"][0]["position"], {"x": 0, "y": 0})

    def test_transform_rejects_invalid_schema_container(self) -> None:
        with self.assertRaises(ValueError):
            _transform_to_pdfme_format({"schemas": "oops"})

    def test_normalize_position_validates_non_negative_values(self) -> None:
        normalized = _normalize_position({"x": "5.5", "y": 2})
        self.assertEqual(normalized, {"x": 5.5, "y": 2.0})

        with self.assertRaises(ValueError):
            _normalize_position({"x": -1, "y": 0})

    def test_build_text_style_maps_supported_attributes(self) -> None:
        content = {
            "fontSize": 18,
            "font": "Courier",
            "bold": True,
            "italic": True,
            "color": "#336699",
            "lineHeight": 1.4,
            "textAlign": "center",
        }

        style = _build_text_style(content)

        self.assertEqual(style["s"], 18.0)
        self.assertEqual(style["f"], "Courier")
        self.assertTrue(style["b"])
        self.assertTrue(style["i"])
        self.assertEqual(style["c"], (0x33 / 255, 0x66 / 255, 0x99 / 255))
        self.assertEqual(style["line_height"], 1.4)
        self.assertEqual(style["text_align"], "c")

    def test_resolve_page_size_handles_aliases_and_tuples(self) -> None:
        self.assertEqual(_resolve_page_size("blank"), "letter")
        self.assertEqual(_resolve_page_size("legal"), "legal")
        self.assertEqual(_resolve_page_size((400, 500)), (400, 500))


class ParseTests(TestCase):
    """Focused tests for the TOON parser."""

    def test_parse_handles_comments_and_booleans(self) -> None:
        toon = """
(
  title: "Doc"
  flag: true
  value: 42
  list: [1, 2, 3]
  # comment to ignore
)
""".strip()

        result = _parse_toon(toon)

        self.assertEqual(result["title"], "Doc")
        self.assertTrue(result["flag"])
        self.assertEqual(result["value"], 42)
        self.assertEqual(result["list"], [1, 2, 3])

    def test_parse_list_of_objects(self) -> None:
        toon = """
(
  schemas: [
    ( content: ( type: "text", text: "A" ), position: ( x: 10, y: 10 ) ),
    ( content: ( type: "text", text: "B" ), position: ( x: 20, y: 20 ) )
  ]
)
""".strip()

        result = _parse_toon(toon)

        self.assertEqual(len(result["schemas"]), 2)
        self.assertEqual(result["schemas"][1]["content"]["text"], "B")

    def test_parse_invalid_structure_raises(self) -> None:
        with self.assertRaises(ValueError):
            _parse_toon("( key value )")

