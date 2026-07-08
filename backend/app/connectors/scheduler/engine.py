import asyncio
from typing import Dict, Any, List

class SyncScheduler:
    """
    Manages the polling and syncing lifecycle for connectors.
    In the future, this might run on Temporal or Celery Beat.
    """
    def __init__(self):
        self.jobs = {}

    async def schedule_sync(self, connector_name: str, interval_seconds: int):
        print(f"[SyncScheduler] Scheduling {connector_name} to sync every {interval_seconds}s")
        # Start an asyncio task for the polling loop
        task = asyncio.create_task(self._sync_loop(connector_name, interval_seconds))
        self.jobs[connector_name] = task

    async def _sync_loop(self, connector_name: str, interval_seconds: int):
        while True:
            print(f"[SyncScheduler] Triggering sync for {connector_name}...")
            # Here we would load the connector and call sync()
            await asyncio.sleep(interval_seconds)
