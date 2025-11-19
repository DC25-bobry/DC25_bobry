from functools import lru_cache
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _get_magic_mime():
    try:
        import magic  # type: ignore
    except Exception as e:
        logger.info("python-magic unavailable: %s", e)
        return None

    try:
        return magic.Magic(mime=True)  # type: ignore[attr-defined]
    except Exception as e:
        logger.warning("Failed to initialize libmagic: %s", e)
        return None

def sniff_mime(content: bytes) -> Optional[str]:
    if not content:
        return None

    m = _get_magic_mime()
    if m is None:
        return None

    try:
        return m.from_buffer(content, mime=True)  # type: ignore[attr-defined]
    except Exception as e:
        logger.error("Failed to determine MIME type: %s", e)
        return None

def guess_ext_from_filename(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else None
