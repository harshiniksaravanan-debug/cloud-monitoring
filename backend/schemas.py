from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class MonitorCreate(BaseModel):
    name: str
    url: str
    check_interval: int = 60


class MonitorUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    check_interval: Optional[int] = None
    is_active: Optional[bool] = None


class MonitorResponse(BaseModel):
    id: int
    name: str
    url: str
    check_interval: int
    is_active: bool
    last_status: Optional[str] = None
    last_checked_at: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    uptime_percentage: Optional[float] = None

    class Config:
        from_attributes = True


class IncidentResponse(BaseModel):
    id: int
    monitor_id: int
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    monitor_name: Optional[str] = None

    class Config:
        from_attributes = True


class IncidentUpdate(BaseModel):
    status: str
    resolved_at: Optional[datetime] = None


class DashboardStats(BaseModel):
    total_monitors: int
    active_monitors: int
    online_count: int
    offline_count: int
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    average_response_time: Optional[float] = None
