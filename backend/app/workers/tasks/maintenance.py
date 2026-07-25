import asyncio
from datetime import datetime, timedelta, timezone
from app.workers.celery_app import celery_app
from app.db.session import async_session_maker
from sqlalchemy import delete
from app.db.models.audit import LoginAuditLog
from app.db.models.telemetry import AILog

@celery_app.task(name="app.workers.tasks.maintenance.purge_old_logs")
def purge_old_logs(days_to_keep: int = 90):
    """
    Purge telemetry and audit logs older than the specified number of days.
    """
    async def _purge():
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        async with async_session_maker() as session:
            # Delete old LoginAuditLog
            await session.execute(
                delete(LoginAuditLog).where(LoginAuditLog.timestamp < cutoff_date)
            )
            # Delete old AILog
            await session.execute(
                delete(AILog).where(AILog.timestamp < cutoff_date)
            )
            await session.commit()
            
    # Run async function in synchronous Celery task
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_purge())
