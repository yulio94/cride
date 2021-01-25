"""Beat tasks configuration"""

# Django
from django.utils import timezone

# Celery
from cride.taskapp.celery import app
from celery import shared_task
from celery.schedules import crontab


# Models
from cride.rides.models import Ride

# Utilities
from datetime import timedelta


@shared_task(name='disable_finished_rides')
def disable_finished_rides():
    """Disable finished rides."""
    now = timezone.now()
    offset = now + timedelta(seconds=5)
    rides = Ride.objects.filter(arrival_date__gte=now,
                                arrival_date__lte=offset,
                                is_active=True)
    rides.update(is_active=False)


app.conf.beat_schedule = {
    'disable-finished-rides': {
        'task': 'disable_finished_rides',
        'schedule': crontab(hour=23)
    }
}
