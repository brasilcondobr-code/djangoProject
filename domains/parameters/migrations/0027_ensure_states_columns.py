from django.db import migrations


def ensure_parameters_columns(apps, schema_editor):
    from django.db import connection

    if connection.vendor != 'postgresql':
        return

    with connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE parameters_states
              ADD COLUMN IF NOT EXISTS capital VARCHAR(100) NULL,
              ADD COLUMN IF NOT EXISTS region VARCHAR(100) NULL,
              ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
              ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
        """)
        cursor.execute("""
            ALTER TABLE parameters_addresses
              ADD COLUMN IF NOT EXISTS neighborhood VARCHAR(255) NULL,
              ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
              ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
        """)
        cursor.execute("""
            ALTER TABLE parameters_typescondominium
              ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
              ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
        """)
        cursor.execute("""
            ALTER TABLE parameters_structioncondominium
              ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
              ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0026_alter_chartofaccountsmaingroup_options'),
    ]

    operations = [
        migrations.RunPython(ensure_parameters_columns, reverse_code=migrations.RunPython.noop),
    ]
