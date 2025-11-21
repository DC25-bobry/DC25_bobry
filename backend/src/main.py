from dotenv import load_dotenv

import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.src.config.logging_config import configure_logging
from backend.src.config.loader import Config
from backend.src.routes.google_drive_route import router as drive_router
from backend.src.routes.upload_route import router as upload_router
from backend.src.routes.job_offers_route import router as job_offers_router
from backend.src.routes.synonym_recognizer_route import router as synonym_recognizer_router
from backend.src.routes.candidates_route import router as candidates_router

configure_logging()
logger = logging.getLogger(__name__)

load_dotenv()
config = Config()

app = FastAPI(title=config.core.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drive_router)
app.include_router(upload_router)
app.include_router(synonym_recognizer_router)
app.include_router(job_offers_router)
app.include_router(candidates_router)


logger.info("🚀 Backend started on %s:%s", config.core.HOST, config.core.PORT)
