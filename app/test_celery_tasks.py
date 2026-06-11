import os
import django
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

app = Celery('project')
app.config_from_object('project.settings', namespace='CELERY')
app.autodiscover_tasks()

print("Registered tasks:")
for name in app.tasks.keys():
    print(f" - {name}")
