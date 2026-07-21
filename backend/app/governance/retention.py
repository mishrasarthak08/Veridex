from datetime import datetime, timedelta, timezone

class RetentionPolicy:
    def __init__(self, days_to_retain: int = 90, legal_hold: bool = False):
        self.days_to_retain = days_to_retain
        self.legal_hold = legal_hold

    def should_delete(self, created_at: datetime) -> bool:
        if self.legal_hold:
            return False
            
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.days_to_retain)
        return created_at < cutoff

    async def sweep_audit_log(self, log_path: str = "audit_trail.jsonl"):
        import os, json, aiofiles
        
        if not os.path.exists(log_path):
            return 0
            
        kept_entries = []
        deleted_count = 0
        
        async with aiofiles.open(log_path, mode='r') as f:
            async for line in f:
                try:
                    entry = json.loads(line)
                    created_at = datetime.fromisoformat(entry["timestamp"])
                    if self.should_delete(created_at):
                        deleted_count += 1
                    else:
                        kept_entries.append(line)
                except Exception:
                    # Keep malformed lines just in case
                    kept_entries.append(line)
                    
        if deleted_count > 0:
            async with aiofiles.open(log_path, mode='w') as f:
                for line in kept_entries:
                    await f.write(line)
                    
        return deleted_count
