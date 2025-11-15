from __future__ import annotations

import pytest

from backend.src.services.document_parsing.parsers import DocxParser


@pytest.fixture()
def parser() -> DocxParser:
    return DocxParser()


@pytest.mark.parametrize(
    "mime,ext,expected",
    [
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", None, True),
        (None, ".docx", True),
        (None, ".DOCX", True),

        ("application/pdf", None, False),
        ("application/pdf", ".pdf", False),
        (None, ".pdf", False),

        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".pdf", True),
        ("application/pdf", ".docx", False),
    ],
)
def test_docx_supports_by_mime_and_ext(parser: DocxParser, mime, ext, expected: bool):
    assert parser.supports(mime=mime, ext=ext) is expected
