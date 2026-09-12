from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


celery_app = Celery(
    "dsa_arcade",
    broker=settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scheduled_tasks",
    ],
)


celery_app.conf.update(
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,

    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    task_track_started=True,
    worker_prefetch_multiplier=1,

    beat_schedule={
        "generate-daily-qotd": {
            "task": "app.tasks.scheduled_tasks.generate_daily_qotd",
            "schedule": crontab(
                hour=0,
                minute=0,
            ),
        },

        "send-qotd-reminders": {
            "task": "app.tasks.scheduled_tasks.send_qotd_reminders",
            "schedule": crontab(
                hour=20,
                minute=0,
            ),
        },
    },
)