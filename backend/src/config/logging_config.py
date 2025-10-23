import logging
from typing import Dict
from colorama import init as colorama_init, Fore, Style

colorama_init()

class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS: Dict[int, str] = {
        logging.DEBUG: Fore.WHITE,
        logging.INFO: Fore.WHITE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        formatted = super().format(record)
        return f"{color}{formatted}{Style.RESET_ALL}"

def configure_logging(level: int = logging.INFO) -> None:
    fmt = "%(asctime)s %(levelname)s %(name)s:\n%(message)s"
    formatter = ColoredFormatter(fmt)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
