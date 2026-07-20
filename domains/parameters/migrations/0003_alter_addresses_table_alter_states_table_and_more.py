from django.db import migrations


RENAME_SQL = """
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'condominium_addresses') THEN
        ALTER TABLE condominium_addresses RENAME TO parameters_addresses;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'condominium_states') THEN
        ALTER TABLE condominium_states RENAME TO parameters_states;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'condominium_structioncondominium') THEN
        ALTER TABLE condominium_structioncondominium RENAME TO parameters_structioncondominium;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'condominium_typescondominium') THEN
        ALTER TABLE condominium_typescondominium RENAME TO parameters_typescondominium;
    END IF;
END $$;
"""

REVERSE_SQL = """
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'parameters_addresses') THEN
        ALTER TABLE parameters_addresses RENAME TO condominium_addresses;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'parameters_states') THEN
        ALTER TABLE parameters_states RENAME TO condominium_states;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'parameters_structioncondominium') THEN
        ALTER TABLE parameters_structioncondominium RENAME TO condominium_structioncondominium;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'parameters_typescondominium') THEN
        ALTER TABLE parameters_typescondominium RENAME TO condominium_typescondominium;
    END IF;
END $$;
"""


def rename_tables(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(RENAME_SQL)


def reverse_rename_tables(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0002_add_state_id_to_addresses'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterModelTable(
                    name='addresses',
                    table=None,
                ),
                migrations.AlterModelTable(
                    name='states',
                    table=None,
                ),
                migrations.AlterModelTable(
                    name='structioncondominium',
                    table=None,
                ),
                migrations.AlterModelTable(
                    name='typescondominium',
                    table=None,
                ),
            ],
            database_operations=[
                migrations.RunPython(rename_tables, reverse_rename_tables),
            ],
        ),
    ]
