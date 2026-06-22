from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db
from models import Incident, Monitor
from schemas import IncidentResponse, IncidentUpdate

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    status: str | None = Query(None),
    severity: str | None = Query(None),
    monitor_id: int | None = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Incident).options(joinedload(Incident.monitor))

    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    if monitor_id:
        query = query.where(Incident.monitor_id == monitor_id)

    query = query.order_by(Incident.detected_at.desc()).limit(limit)
    result = await db.execute(query)
    incidents = result.scalars().all()

    return [
        IncidentResponse(
            id=inc.id,
            monitor_id=inc.monitor_id,
            title=inc.title,
            description=inc.description,
            severity=inc.severity,
            status=inc.status,
            detected_at=inc.detected_at,
            resolved_at=inc.resolved_at,
            response_time_ms=inc.response_time_ms,
            status_code=inc.status_code,
            error_message=inc.error_message,
            monitor_name=inc.monitor.name if inc.monitor else None,
        )
        for inc in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident)
        .options(joinedload(Incident.monitor))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return IncidentResponse(
        id=incident.id,
        monitor_id=incident.monitor_id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        detected_at=incident.detected_at,
        resolved_at=incident.resolved_at,
        response_time_ms=incident.response_time_ms,
        status_code=incident.status_code,
        error_message=incident.error_message,
        monitor_name=incident.monitor.name if incident.monitor else None,
    )


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int, data: IncidentUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Incident)
        .options(joinedload(Incident.monitor))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = data.status
    if data.status == "resolved":
        incident.resolved_at = data.resolved_at or datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(incident)

    return IncidentResponse(
        id=incident.id,
        monitor_id=incident.monitor_id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        detected_at=incident.detected_at,
        resolved_at=incident.resolved_at,
        response_time_ms=incident.response_time_ms,
        status_code=incident.status_code,
        error_message=incident.error_message,
        monitor_name=incident.monitor.name if incident.monitor else None,
    )
