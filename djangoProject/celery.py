import os

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')

app = Celery('djangoProject')

app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.broker_url = ('redis://:password@hostname:port/db_number')

app.autodiscover_tasks()
