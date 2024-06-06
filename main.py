"""The main application module.

Attrs:
    logger: Logger: The app logger instance.
    app (FastAPI): The API app instance."""

import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import router
from app.storage.helpers import init_db


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting the API service...")

    await init_db()
    yield

    logger.info("Stopping the API service...")


app = FastAPI(lifespan=lifespan)
app.include_router(router)
