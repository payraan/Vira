from fastapi import FastAPI

from vira.settings import settings
from infra.logging.logger import setup_logging


setup_logging()

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
