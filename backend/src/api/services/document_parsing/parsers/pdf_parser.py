from __future__ import annotations
import io
import logging
from typing import Optional
from pdfminer.high_level import extract_text as pdfminer_extract

from .document_parser import DocumentParser
from ..exceptions import ExtractionError

logger = logging.getLogger(__name__)


class PdfParser(DocumentParser):
    name = "pdfminer"

    def supports(self, *, mime: Optional[str], ext: Optional[str]) -> bool:
        pdf_mime = "application/pdf"
        if mime is not None:
            return mime == pdf_mime
        return ext is not None and ext.lower() == ".pdf"

    def extract_text(self, content: bytes) -> str:
        try:
            text = pdfminer_extract(io.BytesIO(content))
            if text is None:
                text = ""
            return text
        except Exception as e:
            raise ExtractionError(f"Failed to extract text from PDF: {e}") from e
