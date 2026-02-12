from fastapi import FastAPI
from sqlalchemy import text

from vira.settings import settings
from infra.logging.logger import setup_logging
from infra.db.database import get_engine


setup_logging()

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}

@app.get("/db/health")
async def db_health():
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        # Keep it readable while developing. We'll tighten this later.
        return {"status": "error", "db": "disconnected", "detail": str(e)}
