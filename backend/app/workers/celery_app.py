from celery import Celery
import os

# Use Redis as the message broker and result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "veridex_workers",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks.planner", "app.workers.tasks.agent"]
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
    }
)
