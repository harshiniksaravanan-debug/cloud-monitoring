import asyncio
import logging
from datetime import datetime, timezone

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from config import settings
from database import async_session
from models import Incident, Monitor

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def check_monitor(monitor: Monitor):
    start = datetime.now(timezone.utc)
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(monitor.url, follow_redirects=True)
        elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        if response.status_code < 500:
            new_status = "up"
        else:
            new_status = "down"

        monitor.response_time_ms = round(elapsed, 2)
        monitor.last_checked_at = datetime.now(timezone.utc)

        prev_status = monitor.last_status
        monitor.last_status = new_status

        async with async_session() as db:
            if new_status == "down" and prev_status != "down":
                incident = Incident(
                    monitor_id=monitor.id,
                    title=f"Downtime detected: {monitor.name}",
                    description=(
                        f"Monitor {monitor.name} ({monitor.url}) is down. "
                        f"Status code: {response.status_code}"
                    ),
                    severity="critical",
                    status="open",
                    detected_at=datetime.now(timezone.utc),
                    response_time_ms=round(elapsed, 2),
                    status_code=response.status_code,
                    error_message=(
                        f"HTTP {response.status_code}" if response.status_code >= 400 else None
                    ),
                )
                db.add(incident)
                logger.warning(f"Incident created for {monitor.name} - status {response.status_code}")

            elif new_status == "up" and prev_status == "down":
                result = await db.execute(
                    select(Incident)
                    .where(Incident.monitor_id == monitor.id)
                    .where(Incident.status == "open")
                    .order_by(Incident.detected_at.desc())
                )
                open_incidents = result.scalars().all()
                for inc in open_incidents:
                    inc.status = "resolved"
                    inc.resolved_at = datetime.now(timezone.utc)
                    inc.description = (
                        f"{inc.description}\n\nAuto-resolved at "
                        f"{datetime.now(timezone.utc).isoformat()}"
                    )
                logger.info(f"Incidents auto-resolved for {monitor.name}")

            db.add(monitor)
            await db.commit()

    except httpx.RequestError as e:
        monitor.last_status = "down"
        monitor.last_checked_at = datetime.now(timezone.utc)
        monitor.response_time_ms = None

        async with async_session() as db:
            if monitor.last_status != "down" or True:
                result = await db.execute(
                    select(Incident)
                    .where(Incident.monitor_id == monitor.id)
                    .where(Incident.status == "open")
                )
                existing = result.scalars().first()
                if not existing:
                    incident = Incident(
                        monitor_id=monitor.id,
                        title=f"Connection failed: {monitor.name}",
                        description=str(e),
                        severity="critical",
                        status="open",
                        detected_at=datetime.now(timezone.utc),
                        error_message=str(e),
                    )
                    db.add(incident)
                    logger.warning(f"Incident created for {monitor.name} - connection failed")

            db.add(monitor)
            await db.commit()


async def run_checks():
    async with async_session() as db:
        result = await db.execute(
            select(Monitor).where(Monitor.is_active == True)
        )
        monitors = result.scalars().all()

    tasks = [check_monitor(m) for m in monitors]
    if tasks:
        await asyncio.gather(*tasks)


async def start_monitoring():
    scheduler.add_job(
        run_checks,
        "interval",
        seconds=settings.check_interval_seconds,
        id="health_checks",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Monitoring started - checking every {settings.check_interval_seconds}s"
    )


async def stop_monitoring():
    scheduler.shutdown(wait=False)
    logger.info("Monitoring stopped")
