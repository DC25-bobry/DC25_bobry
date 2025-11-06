from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import logging

from .exceptions import DocumentParsingError, UnsupportedFormatError
from .mime_sniffing import sniff_mime, guess_ext_from_filename
from .parser_registry import ParserRegistry
from .text_cleanup import normalize_text

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ParsedDocument:
    text: str
    mime: Optional[str]
    used_parser: str


class DocumentParsingService:
    def __init__(self, registry: Optional[ParserRegistry] = None, *, max_bytes: int = 50 * 1024 * 1024):
        self._registry = registry or ParserRegistry()
        self._max_bytes = max_bytes

    def extract_text(
        self,
        content: bytes,
        *,
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> ParsedDocument:
        if content is None:
            raise DocumentParsingError("No content provided.")
        if len(content) > self._max_bytes:
            raise DocumentParsingError(f"File too large: should be less than {self._max_bytes} but is {len(content)}.")

        mime = content_type or sniff_mime(content)
        ext = guess_ext_from_filename(filename)

        try:
            parser = self._registry.find(mime=mime, ext=ext)
        except UnsupportedFormatError:
            logger.info("Unsupported format; mime=%s ext=%s", mime, ext)
            raise

        logger.debug("Extracting text using %s", parser.name)
        text = parser.extract_text(content)
        normalized_text = normalize_text(text)
        return ParsedDocument(text=normalized_text, mime=mime, used_parser=parser.name)
