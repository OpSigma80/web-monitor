from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.auth import require_api_auth
from app.models import Monitor, Change
from app.schemas import MonitorCreate, MonitorUpdate, MonitorRead, ChangeRead
from app.workers.tasks import check_monitor

router = APIRouter(
    prefix="/monitors",
    tags=["monitors"],
    dependencies=[Depends(require_api_auth)],
)


@router.post("/", response_model=MonitorRead, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    payload: MonitorCreate,
    session: AsyncSession = Depends(get_session),
):
    monitor = Monitor(
        name=payload.name,
        url=str(payload.url),
        monitor_type=payload.monitor_type,
        css_selector=payload.css_selector,
        xpath=payload.xpath,
        check_interval_minutes=payload.check_interval_minutes,
        threshold_percent=payload.threshold_percent,
    )
    session.add(monitor)
    await session.commit()
    await session.refresh(monitor)
    return monitor


@router.get("/", response_model=List[MonitorRead])
async def list_monitors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Monitor).order_by(Monitor.id))
    return result.scalars().all()


@router.get("/{monitor_id}", response_model=MonitorRead)
async def get_monitor(monitor_id: int, session: AsyncSession = Depends(get_session)):
    monitor = await session.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor no encontrado")
    return monitor


@router.patch("/{monitor_id}", response_model=MonitorRead)
async def update_monitor(
    monitor_id: int,
    payload: MonitorUpdate,
    session: AsyncSession = Depends(get_session),
):
    monitor = await session.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(monitor, key, value)

    session.add(monitor)
    await session.commit()
    await session.refresh(monitor)
    return monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(monitor_id: int, session: AsyncSession = Depends(get_session)):
    monitor = await session.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor no encontrado")
    await session.delete(monitor)
    await session.commit()


@router.post("/{monitor_id}/check")
async def run_monitor_check(monitor_id: int):
    return await check_monitor({}, monitor_id)


@router.get("/{monitor_id}/changes", response_model=List[ChangeRead])
async def list_changes(
    monitor_id: int,
    session: AsyncSession = Depends(get_session),
):
    monitor = await session.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor no encontrado")

    result = await session.execute(
        select(Change)
        .where(Change.monitor_id == monitor_id)
        .order_by(Change.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()