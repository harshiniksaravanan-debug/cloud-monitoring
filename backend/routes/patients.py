from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db
from models import MedicalRecord, Patient
from schemas import (
    DashboardStats,
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Patient.id)))).scalar() or 0
    male = (await db.execute(select(func.count(Patient.id)).where(Patient.gender == "Male"))).scalar() or 0
    female = (await db.execute(select(func.count(Patient.id)).where(Patient.gender == "Female"))).scalar() or 0
    total_records = (await db.execute(select(func.count(MedicalRecord.id)))).scalar() or 0
    active = (await db.execute(select(func.count(MedicalRecord.id)).where(MedicalRecord.status == "ongoing"))).scalar() or 0
    resolved = (await db.execute(select(func.count(MedicalRecord.id)).where(MedicalRecord.status == "resolved"))).scalar() or 0

    return DashboardStats(
        total_patients=total,
        active_records=active,
        resolved_records=resolved,
        total_records=total_records,
        male_count=male,
        female_count=female,
    )


@router.get("", response_model=list[PatientResponse])
async def list_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Patient).order_by(Patient.created_at.desc())
    )
    patients = result.scalars().all()

    responses = []
    for p in patients:
        count = (await db.execute(select(func.count(MedicalRecord.id)).where(MedicalRecord.patient_id == p.id))).scalar() or 0
        resp = PatientResponse.model_validate(p)
        resp.record_count = count
        responses.append(resp)

    return responses


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(data: PatientCreate, db: AsyncSession = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    count = (await db.execute(select(func.count(MedicalRecord.id)).where(MedicalRecord.patient_id == patient.id))).scalar() or 0
    resp = PatientResponse.model_validate(patient)
    resp.record_count = count
    return resp


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int, data: PatientUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)

    await db.commit()
    await db.refresh(patient)
    return PatientResponse.model_validate(patient)


@router.delete("/{patient_id}", status_code=204)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await db.delete(patient)
    await db.commit()


@router.get("/{patient_id}/records", response_model=list[MedicalRecordResponse])
async def list_records(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MedicalRecord)
        .options(joinedload(MedicalRecord.patient))
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.created_at.desc())
    )
    records = result.scalars().all()
    return [
        MedicalRecordResponse(
            id=r.id,
            patient_id=r.patient_id,
            disease_name=r.disease_name,
            symptoms=r.symptoms,
            diagnosis_date=r.diagnosis_date,
            doctor=r.doctor,
            medicines=r.medicines,
            status=r.status,
            notes=r.notes,
            created_at=r.created_at,
            patient_name=r.patient.name if r.patient else None,
        )
        for r in records
    ]


@router.post("/{patient_id}/records", response_model=MedicalRecordResponse, status_code=201)
async def create_record(
    patient_id: int, data: MedicalRecordCreate, db: AsyncSession = Depends(get_db)
):
    p_result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = p_result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    record = MedicalRecord(patient_id=patient_id, **data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return MedicalRecordResponse(
        id=record.id,
        patient_id=record.patient_id,
        disease_name=record.disease_name,
        symptoms=record.symptoms,
        diagnosis_date=record.diagnosis_date,
        doctor=record.doctor,
        medicines=record.medicines,
        status=record.status,
        notes=record.notes,
        created_at=record.created_at,
        patient_name=patient.name,
    )


@router.put("/records/{record_id}", response_model=MedicalRecordResponse)
async def update_record(
    record_id: int, data: MedicalRecordUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MedicalRecord)
        .options(joinedload(MedicalRecord.patient))
        .where(MedicalRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)

    return MedicalRecordResponse(
        id=record.id,
        patient_id=record.patient_id,
        disease_name=record.disease_name,
        symptoms=record.symptoms,
        diagnosis_date=record.diagnosis_date,
        doctor=record.doctor,
        medicines=record.medicines,
        status=record.status,
        notes=record.notes,
        created_at=record.created_at,
        patient_name=record.patient.name if record.patient else None,
    )


@router.delete("/records/{record_id}", status_code=204)
async def delete_record(record_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    await db.delete(record)
    await db.commit()
