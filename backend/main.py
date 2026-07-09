import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import incidents, monitors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

IS_VERCEL = bool(os.environ.get("VERCEL_ENV") or os.environ.get("VERCEL_URL"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await init_db()
    if not IS_VERCEL:
        from services.monitor_service import start_monitoring
        await start_monitoring()
    yield
    if not IS_VERCEL:
        from services.monitor_service import stop_monitoring
        await stop_monitoring()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Cloud Monitoring & Incident Report System",
    version="1.0.0",
    lifespan=lifespan,
)

CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,https://frontend-topaz-sigma-41.vercel.app",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitors.router)
app.include_router(incidents.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "cloud-monitoring"}


if IS_VERCEL:
    @app.post("/api/cron/check")
    async def cron_check():
        from services.monitor_service import run_checks
        await run_checks()
        return {"status": "ok", "message": "Health checks triggered"}

    @app.post("/api/seed")
    async def seed_data():
        from sqlalchemy import select
        from database import async_session
        from models import Monitor
        async with async_session() as db:
            existing = await db.execute(select(Monitor).limit(1))
            if existing.scalar_one_or_none():
                return {"status": "ok", "message": "Data already seeded"}
            monitors = [
                Monitor(name="Google", url="https://www.google.com", check_interval=60),
                Monitor(name="GitHub", url="https://www.github.com", check_interval=60),
                Monitor(name="Example", url="https://example.com", check_interval=60),
            ]
            for m in monitors:
                db.add(m)
            await db.commit()
        return {"status": "ok", "message": "Seed data added"}
