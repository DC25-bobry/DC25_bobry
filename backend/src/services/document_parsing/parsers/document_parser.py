from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParserMatch:
    name: str
    priority: int


class DocumentParser(ABC):
    """
    Strategy interface - implementations should be stateless singletons.
    """
    name: str = "base"

    @abstractmethod
    def supports(self, *, mime: Optional[str], ext: Optional[str]) -> bool:
        """Does parser support file by mime-type or fallback extension"""

    @abstractmethod
    def extract_text(self, content: bytes) -> str:
        """Returns contents of file as plain text"""
