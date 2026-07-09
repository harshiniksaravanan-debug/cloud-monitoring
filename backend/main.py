import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import patients

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await init_db()
    yield
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Hospital Patient & Disease Management System",
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

app.include_router(patients.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "hospital-management"}


@app.post("/api/seed")
async def seed_data():
    from sqlalchemy import select
    from database import async_session
    from models import Patient, MedicalRecord
    from datetime import datetime, timezone
    async with async_session() as db:
        existing = await db.execute(select(Patient).limit(1))
        if existing.scalar_one_or_none():
            return {"status": "ok", "message": "Data already seeded"}
        p1 = Patient(name="John Doe", age=45, gender="Male", contact="+1-555-0101",
                     blood_group="A+", allergies="Penicillin", height=175.0, weight=80.0,
                     emergency_contact="+1-555-0199")
        p2 = Patient(name="Jane Smith", age=32, gender="Female", contact="+1-555-0102",
                     blood_group="O-", allergies="None", height=162.0, weight=58.0,
                     emergency_contact="+1-555-0198")
        db.add(p1)
        db.add(p2)
        await db.flush()
        r1 = MedicalRecord(patient_id=p1.id, disease_name="Type 2 Diabetes",
                           symptoms="Increased thirst, frequent urination, fatigue",
                           diagnosis_date=datetime(2026, 3, 15, tzinfo=timezone.utc),
                           doctor="Dr. Sarah Johnson", medicines="Metformin 500mg",
                           status="ongoing", notes="Monitor blood sugar levels weekly")
        r2 = MedicalRecord(patient_id=p2.id, disease_name="Migraine",
                           symptoms="Severe headache, nausea, light sensitivity",
                           diagnosis_date=datetime(2026, 6, 1, tzinfo=timezone.utc),
                           doctor="Dr. Michael Chen", medicines="Sumatriptan 50mg as needed",
                           status="ongoing", notes="Avoid triggers, maintain sleep schedule")
        db.add(r1)
        db.add(r2)
        await db.commit()
    return {"status": "ok", "message": "Seed data added"}
