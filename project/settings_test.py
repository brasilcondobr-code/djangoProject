import os
import tempfile
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

# Isolate media files created by tests (uploads) from the real MEDIA_ROOT
MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="brasilcondo_test_media_"))

# Disable some features that might interfere with tests or require external services
DEBUG = True
CELERY_BROKER_URL = 'memory://'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
