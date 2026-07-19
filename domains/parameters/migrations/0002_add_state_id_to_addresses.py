from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "ALTER TABLE condominium_addresses ADD COLUMN IF NOT EXISTS state_id bigint NOT NULL;",
                        "ALTER TABLE condominium_addresses ADD CONSTRAINT condominium_addresses_state_id_fk FOREIGN KEY (state_id) REFERENCES condominium_states (id) DEFERRABLE INITIALLY DEFERRED;",
                        "ALTER TABLE condominium_addresses ADD COLUMN IF NOT EXISTS neighborhood varchar(255) NULL;",
                        "ALTER TABLE condominium_addresses ALTER COLUMN complement DROP NOT NULL;",
                        "ALTER TABLE condominium_addresses ALTER COLUMN number TYPE integer USING number::integer;",
                        "ALTER TABLE condominium_states ADD COLUMN IF NOT EXISTS capital varchar(100) NULL;",
                        "ALTER TABLE condominium_states ADD COLUMN IF NOT EXISTS region varchar(100) NULL;",
                        "ALTER TABLE condominium_states ADD COLUMN IF NOT EXISTS created_at timestamp with time zone NULL;",
                        "ALTER TABLE condominium_states ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NULL;",
                        "ALTER TABLE condominium_structioncondominium ADD COLUMN IF NOT EXISTS created_at timestamp with time zone NULL;",
                        "ALTER TABLE condominium_structioncondominium ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NULL;",
                        "ALTER TABLE condominium_typescondominium ADD COLUMN IF NOT EXISTS created_at timestamp with time zone NULL;",
                        "ALTER TABLE condominium_typescondominium ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NULL;",
                    ],
                    reverse_sql=[
                        "ALTER TABLE condominium_addresses DROP CONSTRAINT IF EXISTS condominium_addresses_state_id_fk;",
                        "ALTER TABLE condominium_addresses DROP COLUMN IF EXISTS state_id;",
                        "ALTER TABLE condominium_addresses DROP COLUMN IF EXISTS neighborhood;",
                        "ALTER TABLE condominium_addresses ALTER COLUMN complement SET NOT NULL;",
                        "ALTER TABLE condominium_addresses ALTER COLUMN number TYPE varchar USING number::varchar;",
                        "ALTER TABLE condominium_states DROP COLUMN IF EXISTS capital;",
                        "ALTER TABLE condominium_states DROP COLUMN IF EXISTS region;",
                        "ALTER TABLE condominium_states DROP COLUMN IF EXISTS created_at;",
                        "ALTER TABLE condominium_states DROP COLUMN IF EXISTS updated_at;",
                        "ALTER TABLE condominium_structioncondominium DROP COLUMN IF EXISTS created_at;",
                        "ALTER TABLE condominium_structioncondominium DROP COLUMN IF EXISTS updated_at;",
                        "ALTER TABLE condominium_typescondominium DROP COLUMN IF EXISTS created_at;",
                        "ALTER TABLE condominium_typescondominium DROP COLUMN IF EXISTS updated_at;",
                    ],
                ),
            ],
            state_operations=[],
        ),
    ]
