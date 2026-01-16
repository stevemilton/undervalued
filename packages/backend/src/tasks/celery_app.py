"""Celery application configuration."""

from celery import Celery

from ..config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "undervalued",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.tasks.ingestion"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes hard limit

    # Result expiration
    result_expires=3600,  # 1 hour

    # Beat schedule for periodic tasks
    beat_schedule={
        "refresh-opportunities-daily": {
            "task": "src.tasks.ingestion.refresh_all_opportunities",
            "schedule": 86400.0,  # Every 24 hours
        },
    },
)


def get_celery_app() -> Celery:
    """Get the Celery application instance."""
    return celery_app
