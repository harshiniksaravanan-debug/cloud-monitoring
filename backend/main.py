import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import incidents, monitors
from services.monitor_service import start_monitoring, stop_monitoring

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await init_db()
    await start_monitoring()
    yield
    await stop_monitoring()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Cloud Monitoring & Incident Report System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitors.router)
app.include_router(incidents.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "cloud-monitoring"}
