"""
Tareas en background con ARQ.
"""

from datetime import datetime, timezone
from sqlmodel import select
from arq.connections import RedisSettings
from arq.cron import cron

from app.database import AsyncSessionLocal
from app.models import Monitor, Snapshot, Change, MonitorStatus
from app.services.scraper import extract_value
from app.services.detector import has_significant_change, build_summary
from app.services.notifier import notify_change
from app.config import settings


async def check_monitor(ctx, monitor_id: int):
    async with AsyncSessionLocal() as session:
        monitor = await session.get(Monitor, monitor_id)
        if not monitor or not monitor.is_active:
            return {"status": "skipped", "reason": "inactive or not found"}

        try:
            value, html = await extract_value(
                url=str(monitor.url),
                css_selector=monitor.css_selector,
                xpath=monitor.xpath,
                use_playwright=False,
                monitor_type=monitor.monitor_type.value,
            )

            if value is None:
                monitor.status = MonitorStatus.ERROR
                monitor.last_checked_at = datetime.now(timezone.utc)
                session.add(monitor)
                await session.commit()
                return {"status": "error", "reason": "value not found"}

            snapshot = Snapshot(
                monitor_id=monitor.id,
                value=value,
                raw_html=None,
            )
            session.add(snapshot)

            changed = (
                False
                if monitor.last_value is None
                else has_significant_change(
                    old_value=monitor.last_value,
                    new_value=value,
                    threshold_percent=monitor.threshold_percent,
                )
            )

            if changed and monitor.last_value is not None:
                summary = build_summary(
                    monitor_name=monitor.name,
                    old_value=monitor.last_value,
                    new_value=value,
                    monitor_type=monitor.monitor_type.value,
                )
                change = Change(
                    monitor_id=monitor.id,
                    old_value=monitor.last_value,
                    new_value=value,
                    summary=summary,
                    notified=False,
                )
                session.add(change)

                notified = await notify_change(summary=summary, url=str(monitor.url))
                change.notified = notified

            monitor.last_value = value
            monitor.last_checked_at = datetime.now(timezone.utc)
            monitor.status = MonitorStatus.ACTIVE
            session.add(monitor)

            await session.commit()
            return {
                "status": "ok",
                "changed": changed,
                "value": value,
            }

        except Exception as e:
            monitor.status = MonitorStatus.ERROR
            monitor.last_checked_at = datetime.now(timezone.utc)
            session.add(monitor)
            await session.commit()
            return {"status": "error", "reason": str(e)}


async def check_all_due_monitors(ctx):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Monitor).where(Monitor.is_active == True)
        )
        monitors = result.scalars().all()

        enqueued = 0
        for monitor in monitors:
            should_check = True
            if monitor.last_checked_at:
                delta = datetime.now(timezone.utc) - monitor.last_checked_at.replace(tzinfo=timezone.utc)
                should_check = delta.total_seconds() >= monitor.check_interval_minutes * 60

            if should_check:
                await ctx["redis"].enqueue_job("check_monitor", monitor.id)
                enqueued += 1

        return {"enqueued": enqueued}


def get_redis_settings() -> RedisSettings:
    url = settings.redis_url
    if url.startswith("redis://"):
        url = url[len("redis://"):]
    host_port = url.split("/")[0]
    if ":" in host_port:
        host, port = host_port.split(":")
        return RedisSettings(host=host, port=int(port))
    return RedisSettings(host=host_port)


class WorkerSettings:
    functions = [check_monitor, check_all_due_monitors]
    redis_settings = get_redis_settings()
    cron_jobs = [
        cron(
            check_all_due_monitors,
            minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55},
            run_at_startup=True,
        ),
    ]