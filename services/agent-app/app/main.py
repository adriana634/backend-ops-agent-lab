from fastapi import FastAPI
import logging

from app.api.routes import router
from app.config import get_settings

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
	datefmt="%Y-%m-%dT%H:%M:%S",
	force=True,
)

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(router)
