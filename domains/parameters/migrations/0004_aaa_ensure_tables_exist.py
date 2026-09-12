from django.db import migrations
from django.db.utils import OperationalError


def ensure_tables_exist(apps, schema_editor):
    from django.db import connection

    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parameters_states (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    abbreviation VARCHAR(2) NOT NULL UNIQUE,
                    capital VARCHAR(100) NULL,
                    region VARCHAR(100) NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parameters_typescondominium (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parameters_structioncondominium (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parameters_addresses (
                    id BIGSERIAL PRIMARY KEY,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    zip_code VARCHAR(20) NOT NULL,
                    street VARCHAR(255) NOT NULL,
                    number INTEGER NOT NULL,
                    complement VARCHAR(255) NULL,
                    neighborhood VARCHAR(255) NULL,
                    city VARCHAR(100) NOT NULL,
                    state_id BIGINT REFERENCES parameters_states(id) DEFERRABLE INITIALLY DEFERRED,
                    country VARCHAR(100) NOT NULL DEFAULT 'Brasil',
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """)
        return

    for model_name in ['States', 'TypesCondominium', 'StructionCondominium', 'Addresses']:
        model = apps.get_model('parameters', model_name)
        try:
            schema_editor.create_model(model)
        except OperationalError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0003_alter_addresses_table_alter_states_table_and_more'),
    ]

    operations = [
        migrations.RunPython(ensure_tables_exist, migrations.RunPython.noop),
    ]
