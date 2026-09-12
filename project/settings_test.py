import os
from pathlib import Path
from .settings import *

# Override database to use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Allow test client to access localhost without depending on env vars
ALLOWED_HOSTS = ['*']

# Disable some features that might interfere with tests or require external services
DEBUG = True
CELERY_BROKER_URL = 'memory://'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
