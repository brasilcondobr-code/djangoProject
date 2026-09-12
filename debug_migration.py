import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
from django.conf import settings

# Create a test database
from django.test.utils import setup_databases, setup_test_environment, teardown_databases

class DebugDB:
    def __init__(self):
        self.old_config = None

    def setup(self):
        setup_test_environment()
        self.old_config = setup_databases(verbosity=0, interactive=False, keepdb=False)
        # Check tables after migration
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
            tables = [r[0] for r in cursor.fetchall()]
            print("Tables created after migration:")
            for t in sorted(tables):
                print(f"  {t}")
            # Check specific
            for tname in ['condominium_addresses', 'parameters_addresses', 'condominium_condominium', 'condominium_typescondominium', 'parameters_typescondominium']:
                cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", [tname])
                exists = cursor.fetchone()[0]
                print(f"{tname}: {'EXISTS' if exists else 'MISSING'}")

    def teardown(self):
        teardown_databases(self.old_config, verbosity=0)

if __name__ == '__main__':
    d = DebugDB()
    try:
        d.setup()
    finally:
        d.teardown()
