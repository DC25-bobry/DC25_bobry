from dotenv import load_dotenv

import logging
from fastapi import FastAPI

from backend.src.config.logging_config import configure_logging
from backend.src.config.loader import Config
from backend.src.routes.google_drive_route import router as drive_router
from backend.src.routes.upload_route import router as upload_router
from backend.src.routes.synonym_recognizer_route import router as synonym_recognizer_router

configure_logging()
logger = logging.getLogger(__name__)

load_dotenv()
config = Config()

app = FastAPI(title=config.core.APP_NAME)

app.include_router(drive_router)
app.include_router(upload_router)
app.include_router(synonym_recognizer_router)

logger.info("🚀 Backend started on %s:%s", config.core.HOST, config.core.PORT)
