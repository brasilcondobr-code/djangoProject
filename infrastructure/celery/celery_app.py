import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Using a namespace 'CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix.
app.config_from_object('project.settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
