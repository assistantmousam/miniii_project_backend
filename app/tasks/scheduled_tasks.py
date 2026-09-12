from app.tasks.celery_app import celery_app


@celery_app.task
def test_background_task() -> str:
    return "DSA Arcade background task is working"


@celery_app.task
def generate_daily_qotd() -> str:
    return "Daily QotD task executed"


@celery_app.task
def send_qotd_reminders() -> str:
    return "QotD reminder task executed"