import logging
import os
import sys
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import incidents, monitors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

is_vercel = os.environ.get("VERCEL", False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Vercel function...")
    await init_db()
    yield
    logger.info("Shutdown.")


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
