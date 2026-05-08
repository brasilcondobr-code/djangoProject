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
                    ],
                    reverse_sql=[
                        "ALTER TABLE condominium_addresses DROP CONSTRAINT IF EXISTS condominium_addresses_state_id_fk;",
                        "ALTER TABLE condominium_addresses DROP COLUMN IF EXISTS state_id;",
                    ],
                ),
            ],
            state_operations=[],
        ),
    ]
