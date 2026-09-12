from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="SELECT 1;",
                    reverse_sql="SELECT 1;",
                ),
            ],
            state_operations=[],
        ),
    ]
