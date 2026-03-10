from celery import Celery
from backend.app.config import config
from celery.schedules import crontab

celery_app_dev = Celery(
    "dev_celery_tasks",
    broker=config.redis_config.broker_url,
    backend=config.redis_config.backend_url,
)

celery_app_dev.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Tashkent",
    enable_utc=True,
    include=["celery_tasks.tasks"],
)


# Для локальной разработки (REMINDER_USE_MINUTES=true): каждую минуту
# Для продакшена: каждые 3 часа
_beat_schedule = (
    crontab(minute="*/1")  # каждую минуту
    if config.reminder_config.use_minutes
    else crontab(minute=0, hour="*/3")  # каждые 3 часа
)
celery_app_dev.conf.beat_schedule = {
    "send_reminder": {
        "task": "celery_tasks.tasks.remind_agent_to_update_advertisement_by_date",
        "schedule": _beat_schedule,
    }
}
