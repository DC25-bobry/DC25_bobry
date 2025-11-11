from pathlib import Path


def get_app_root(anchor_name="backend") -> Path:
    current = Path(__file__).resolve().parent
    while True:
        if (current / anchor_name).exists():
            return current
        if current.parent == current:
            raise RuntimeError(f"Could not find app root containing '{anchor_name}'")
        current = current.parent