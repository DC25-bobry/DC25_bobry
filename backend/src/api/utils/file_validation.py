from typing import Tuple

allowed_MIME = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
}

max_size = 1024 * 1024 * 50 # 50 MB

def validate_file(file_bytes: bytes, filename: str, content_type: str) -> Tuple[bool, str]:
    message = f"{filename}: "
    valid = True
    if len(file_bytes) > max_size:
        message += "Wrong file size. "
        valid = False
    if content_type not in allowed_MIME:
        message += "Wrong content type."
        valid = False

    if valid:
        message += "OK"

    return valid, message
