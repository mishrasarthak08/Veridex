from celery import Celery
from app.core.config import settings

# Use Redis as the message broker and result backend
REDIS_URL = f"redis://{settings.REDIS_SERVER}:{settings.REDIS_PORT}/0"

celery_app = Celery(
    "veridex_workers",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks.planner", "app.workers.tasks.agent", "app.workers.tasks.ingestion"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.workers.tasks.planner.*": {"queue": "planner_queue"},
        "app.workers.tasks.agent.*": {"queue": "agent_queue"},
        "app.workers.tasks.ingestion.*": {"queue": "ingestion_queue"},
    }
)
