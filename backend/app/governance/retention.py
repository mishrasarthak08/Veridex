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
