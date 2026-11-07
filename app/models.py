from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import DateTime, func


class MonitorType(str, Enum):
    PRICE = "price"
    AVAILABILITY = "availability"
    TEXT = "text"
    SELECTOR = "selector"


class MonitorStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class Monitor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url: str
    monitor_type: MonitorType = Field(default=MonitorType.SELECTOR)
    css_selector: Optional[str] = None
    xpath: Optional[str] = None
    check_interval_minutes: int = Field(default=60)
    threshold_percent: Optional[float] = Field(default=None)
    is_active: bool = Field(default=True)
    status: MonitorStatus = Field(default=MonitorStatus.ACTIVE)
    last_value: Optional[str] = Field(default=None, sa_column=Column(Text))
    last_checked_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    )


class Snapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monitor_id: int = Field(foreign_key="monitor.id", index=True)
    value: str = Field(sa_column=Column(Text))
    raw_html: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )


class Change(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monitor_id: int = Field(foreign_key="monitor.id", index=True)
    old_value: Optional[str] = Field(default=None, sa_column=Column(Text))
    new_value: str = Field(sa_column=Column(Text))
    summary: str = Field(sa_column=Column(Text))
    notified: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )