from __future__ import annotations
import logging
from typing import Iterable, List, Optional, Type

from .exceptions import UnsupportedFormatError
from .parsers.document_parser import DocumentParser
from .parsers.pdf_parser import PdfParser
from .parsers.docx_parser import DocxParser

logger = logging.getLogger(__name__)


class ParserRegistry:
    def __init__(self, parsers: Optional[Iterable[DocumentParser]] = None):
        self._parsers: List[DocumentParser] = list(parsers or [
            PdfParser(),
            DocxParser(),
        ])

    def find(self, *, mime: Optional[str], ext: Optional[str]) -> DocumentParser:
        candidates = [p for p in self._parsers if p.supports(mime=mime, ext=ext)]
        if not candidates:
            raise UnsupportedFormatError(f"No parser for mime={mime!r}, ext={ext!r}")
        chosen = candidates[0]
        logger.debug("Chosen parser %s for mime=%s ext=%s",
                     chosen.name, mime, ext)
        return chosen
