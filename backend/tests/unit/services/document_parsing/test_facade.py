from __future__ import annotations
from pathlib import Path

import pytest

from backend.src.api.services.document_parsing import DocumentParsingService


TEST_DIR = Path(__file__).resolve().parent
EXPECTED_TXT = TEST_DIR / "ref_valid_1.txt"
PDF_PATH = Path(__file__).resolve().parents[5] / "test_CVs" / "pdf" / "Valid_1.pdf"
DOCX_PATH = Path(__file__).resolve().parents[5] / "test_CVs" / "docx" / "Valid_1.docx"

@pytest.fixture(scope="module")
def expected_text() -> str:
    if not EXPECTED_TXT.exists():
        pytest.fail(f"Expected reference text file not found: {EXPECTED_TXT}")
    content = EXPECTED_TXT.read_text(encoding="utf-8")
    if not content:
        pytest.fail("Expected reference text file is empty.")
    return content


@pytest.mark.parametrize(
    "bin_path, filename, content_type, expected_parser",
    [
        (PDF_PATH, "Valid_1.pdf", "application/pdf", {"pdfminer"}),
        (DOCX_PATH, "Valid_1.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", {"python-docx"})
    ],
)
def test_parses_valid_documents(bin_path: Path, filename: str, content_type: str, expected_parser: set[str], expected_text: str):
    if not bin_path.exists():
        pytest.fail(f"Input file not found: {bin_path}")
    content = bin_path.read_bytes()
    if not content:
        pytest.fail(f"Input file is empty: {bin_path}")

    sut = DocumentParsingService()
    parsed = sut.extract_text(content, filename=filename, content_type=content_type)

    assert parsed.used_parser in expected_parser
    assert isinstance(parsed.text, str)
    assert parsed.text == expected_text
