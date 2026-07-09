from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    contact: str
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    emergency_contact: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    emergency_contact: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    contact: str
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    emergency_contact: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    record_count: int = 0

    class Config:
        from_attributes = True


class MedicalRecordCreate(BaseModel):
    disease_name: str
    symptoms: Optional[str] = None
    diagnosis_date: Optional[datetime] = None
    doctor: Optional[str] = None
    medicines: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordUpdate(BaseModel):
    disease_name: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis_date: Optional[datetime] = None
    doctor: Optional[str] = None
    medicines: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    disease_name: str
    symptoms: Optional[str] = None
    diagnosis_date: Optional[datetime] = None
    doctor: Optional[str] = None
    medicines: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    patient_name: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_patients: int
    active_records: int
    resolved_records: int
    total_records: int
    male_count: int
    female_count: int
