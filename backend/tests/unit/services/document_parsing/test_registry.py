from __future__ import annotations

import pytest

from backend.src.api.services.document_parsing import UnsupportedFormatError
from backend.src.api.services.document_parsing.parser_registry import ParserRegistry


@pytest.fixture()
def reg() -> ParserRegistry:
    return ParserRegistry()


@pytest.mark.parametrize(
    "mime,ext,expected_name",
    [
        ("application/pdf", None, {"pdfminer"}),
        (None, ".pdf", {"pdfminer"}),
        (None, ".PDF", {"pdfminer"}),

        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", None, {"python-docx"}),
        (None, ".docx", {"python-docx"}),
        (None, ".DOCX", {"python-docx"}),

        ("application/pdf", ".docx", {"pdfminer"}),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".pdf", {"python-docx"}),
    ],
)
def test_registry_selects_parser(reg: ParserRegistry, mime, ext, expected_name):
    parser = reg.find(mime=mime, ext=ext)
    assert parser.name in expected_name


def test_registry_raises_for_unknown_type(reg: ParserRegistry):
    with pytest.raises(UnsupportedFormatError):
        reg.find(mime="application/zip", ext=".zip")


def test_registry_raises_when_both_missing(reg: ParserRegistry):
    with pytest.raises(UnsupportedFormatError):
        reg.find(mime=None, ext=None)
