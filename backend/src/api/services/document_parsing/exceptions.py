class DocumentParsingError(RuntimeError):
    """Unspecified error during document parsing."""


class UnsupportedFormatError(DocumentParsingError):
    """Given document format is not supported for parsing."""


class ExtractionError(DocumentParsingError):
    """Error during content extraction from the document."""
