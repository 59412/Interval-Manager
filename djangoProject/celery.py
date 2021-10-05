"""Celery initialization module"""
import os
# not very secure
import subprocess

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')

app = Celery('djangoProject')

app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.broker_url = ('redis://:password@hostname:port/db_number')

app.autodiscover_tasks()

subprocess.run(["celery", "-A", "djangoProject", "worker",
                "-l", "INFO",
                "--without-gossip",
                "--without-mingle",
                "--without-heartbeat",
                "-Ofair",
                "--pool=solo"])


