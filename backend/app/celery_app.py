from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "event_booking",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.email",
        "app.tasks.qr_codes",
        "app.tasks.bookings",
        "app.tasks.payments",
        "app.tasks.analytics"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Release expired ticket holds every 5 minutes
    "release-expired-holds": {
        "task": "app.tasks.bookings.release_expired_holds",
        "schedule": 300.0,  # 5 minutes
    },
    # Send event reminders 24 hours before
    "send-event-reminders": {
        "task": "app.tasks.email.send_event_reminders",
        "schedule": 3600.0,  # 1 hour
    },
    # Update analytics data every hour
    "update-analytics": {
        "task": "app.tasks.analytics.update_analytics",
        "schedule": 3600.0,  # 1 hour
    },
    # Clean up old sessions every 6 hours
    "cleanup-sessions": {
        "task": "app.tasks.bookings.cleanup_old_sessions",
        "schedule": 21600.0,  # 6 hours
    },
}

# Optional: Configure routing
celery_app.conf.task_routes = {
    "app.tasks.email.*": {"queue": "email"},
    "app.tasks.qr_codes.*": {"queue": "qr_codes"},
    "app.tasks.bookings.*": {"queue": "bookings"},
    "app.tasks.payments.*": {"queue": "payments"},
    "app.tasks.analytics.*": {"queue": "analytics"},
}

# Optional: Configure task priorities
celery_app.conf.task_default_priority = 5
celery_app.conf.worker_direct = True
