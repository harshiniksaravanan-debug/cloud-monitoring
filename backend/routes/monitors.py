from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Incident, Monitor
from schemas import (
    DashboardStats,
    MonitorCreate,
    MonitorResponse,
    MonitorUpdate,
)

router = APIRouter(prefix="/api/monitors", tags=["Monitors"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Monitor.id)))).scalar() or 0
    active = (
        await db.execute(
            select(func.count(Monitor.id)).where(Monitor.is_active == True)
        )
    ).scalar() or 0
    online = (
        await db.execute(
            select(func.count(Monitor.id)).where(Monitor.last_status == "up")
        )
    ).scalar() or 0
    offline = (
        await db.execute(
            select(func.count(Monitor.id)).where(Monitor.last_status == "down")
        )
    ).scalar() or 0
    total_inc = (
        await db.execute(select(func.count(Incident.id)))
    ).scalar() or 0
    open_inc = (
        await db.execute(
            select(func.count(Incident.id)).where(Incident.status == "open")
        )
    ).scalar() or 0
    resolved_inc = (
        await db.execute(
            select(func.count(Incident.id)).where(Incident.status == "resolved")
        )
    ).scalar() or 0
    avg_resp = (
        await db.execute(
            select(func.avg(Monitor.response_time_ms)).where(
                Monitor.last_status == "up"
            )
        )
    ).scalar()

    return DashboardStats(
        total_monitors=total,
        active_monitors=active,
        online_count=online,
        offline_count=offline,
        total_incidents=total_inc,
        open_incidents=open_inc,
        resolved_incidents=resolved_inc,
        average_response_time=round(avg_resp, 2) if avg_resp else None,
    )


@router.get("", response_model=list[MonitorResponse])
async def list_monitors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Monitor).order_by(Monitor.created_at.desc()))
    monitors = result.scalars().all()

    responses = []
    for m in monitors:
        total = (
            await db.execute(
                select(func.count(Incident.id)).where(Incident.monitor_id == m.id)
            )
        ).scalar() or 0
        down_count = (
            await db.execute(
                select(func.count(Incident.id))
                .where(Incident.monitor_id == m.id)
                .where(Incident.severity == "critical")
            )
        ).scalar() or 0
        uptime_pct = round(((total - down_count) / total * 100) if total > 0 else 100, 2)

        resp = MonitorResponse.model_validate(m)
        resp.uptime_percentage = uptime_pct
        responses.append(resp)

    return responses


@router.post("", response_model=MonitorResponse, status_code=201)
async def create_monitor(data: MonitorCreate, db: AsyncSession = Depends(get_db)):
    monitor = Monitor(
        name=data.name,
        url=data.url,
        check_interval=data.check_interval,
    )
    db.add(monitor)
    await db.commit()
    await db.refresh(monitor)
    return MonitorResponse.model_validate(monitor)


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Monitor).where(Monitor.id == monitor_id))
    monitor = result.scalar_one_or_none()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return MonitorResponse.model_validate(monitor)


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(
    monitor_id: int, data: MonitorUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Monitor).where(Monitor.id == monitor_id))
    monitor = result.scalar_one_or_none()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(monitor, key, value)

    await db.commit()
    await db.refresh(monitor)
    return MonitorResponse.model_validate(monitor)


@router.delete("/{monitor_id}", status_code=204)
async def delete_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Monitor).where(Monitor.id == monitor_id))
    monitor = result.scalar_one_or_none()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    await db.delete(monitor)
    await db.commit()
