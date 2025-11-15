from __future__ import annotations

import pytest

from backend.src.services.document_parsing.parsers import PdfParser


@pytest.fixture()
def parser() -> PdfParser:
    return PdfParser()


@pytest.mark.parametrize(
    "mime,ext,expected",
    [
        ("application/pdf", None, True),
        (None, ".pdf", True),
        (None, ".PDF", True),

        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", None, False),
        (None, ".docx", False),

        ("application/pdf", ".docx", True),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".pdf", False),
    ],
)
def test_pdf_supports_by_mime_and_ext(parser: PdfParser, mime, ext, expected: bool):
    assert parser.supports(mime=mime, ext=ext) is expected
