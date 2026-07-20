import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

import django
django.setup()

from django.db import connection
from django.core.management import call_command

# Create test database
from django.test.utils import setup_test_environment
old_config = setup_test_environment()
test_db_name = 'test_debug_' + os.environ.get('USER', 'db')

try:
    call_command('migrate', run_syncdb=True, verbosity=3)
except Exception as e:
    print(f"\nError during migrate: {e}")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        tables = [r[0] for r in cursor.fetchall()]
        print("\nTables that exist:")
        for t in tables:
            print(f"  {t}")
finally:
    pass
