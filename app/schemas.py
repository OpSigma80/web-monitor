from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

from app.models import MonitorType, MonitorStatus


class MonitorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url: HttpUrl
    monitor_type: MonitorType = MonitorType.SELECTOR
    css_selector: Optional[str] = None
    xpath: Optional[str] = None
    check_interval_minutes: int = Field(default=60, ge=5, le=1440)
    threshold_percent: Optional[float] = Field(default=None, ge=0)


class MonitorUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    css_selector: Optional[str] = None
    xpath: Optional[str] = None
    check_interval_minutes: Optional[int] = Field(default=None, ge=5, le=1440)
    threshold_percent: Optional[float] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class MonitorRead(BaseModel):
    id: int
    name: str
    url: str
    monitor_type: MonitorType
    css_selector: Optional[str]
    xpath: Optional[str]
    check_interval_minutes: int
    threshold_percent: Optional[float]
    is_active: bool
    status: MonitorStatus
    last_value: Optional[str]
    last_checked_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ChangeRead(BaseModel):
    id: int
    monitor_id: int
    old_value: Optional[str]
    new_value: str
    summary: str
    notified: bool
    created_at: datetime

    class Config:
        from_attributes = True