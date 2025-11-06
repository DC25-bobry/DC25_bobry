from __future__ import annotations
import re
from typing import Iterable

_CTRL_CHARS_EXCEPT_NT = (
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"
)
_CTRL_PATTERN = re.compile(_CTRL_CHARS_EXCEPT_NT)

_TRAILING_WS_PATTERN = re.compile(r"[ \t]+$", re.MULTILINE)

def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _CTRL_PATTERN.sub("", text)
    text = _TRAILING_WS_PATTERN.sub("", text)

    lines: Iterable[str] = text.split("\n")
    lines = (ln for ln in lines if ln.strip() != "")
    cleaned = "\n".join(lines)

    return cleaned.strip()
