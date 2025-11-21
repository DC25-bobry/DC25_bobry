import pprint
import logging
from pydantic import ValidationError

from .settings.core import CoreSettings
from .settings.google_drive import GoogleDriveSettings
from .settings.smtp import SMTPSettings

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        try:
            self.core = CoreSettings()
            self.google_drive = GoogleDriveSettings()
            self.smtp = SMTPSettings()

            logger.info("✅ Configuration loaded successfully")
        except ValidationError as e:
            logger.error("❌ Configuration validation error", exc_info=e)
            for error in e.errors():
                logger.error("%s: %s", error.get("loc"), error.get("msg"))
            raise SystemExit(1)

    def to_dict(self):
        return {
            "core": self.core.model_dump(),
            "google_drive": self.google_drive.model_dump(),
            "smtp": self.smtp.summary(),
        }
