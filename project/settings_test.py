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

# Disable some features that might interfere with tests or require external services
DEBUG = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'django.db.backends.dummy'
