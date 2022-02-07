import os
from celery import Celery
# Set the default Django settings module for the 'celery' program.
# from .settings import CELERY_RESULT_BACKEND

from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicon.settings')

app = Celery('bicon')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.config_from_object(settings, namespace='CELERY')
# app.conf.result_backend = CELERY_RESULT_BACKEND

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

