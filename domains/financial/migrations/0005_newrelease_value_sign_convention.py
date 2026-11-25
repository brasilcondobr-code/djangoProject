from django.db import migrations, models
from django.db.models import F


def invert_value_sign(apps, schema_editor):
    """Inverte o sinal dos lançamentos existentes.

    A convenção passa de "débito negativo/crédito positivo" para "débito
    positivo/crédito negativo". A operação é idempotente apenas quando
    executada uma única vez por sentido da migration; a reversão usa a mesma
    função.
    """
    NewRelease = apps.get_model("financial", "NewRelease")
    NewRelease.objects.filter(value__isnull=False).update(value=-F("value"))


class Migration(migrations.Migration):

    dependencies = [
        ("financial", "0004_collection_fields_and_payments"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="newrelease",
            name="ck_newrelease_value_sign_matches_launch_type",
        ),
        migrations.RunPython(
            invert_value_sign,
            invert_value_sign,
        ),
        migrations.AlterField(
            model_name="newrelease",
            name="value",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text=(
                    "Informe o valor sem o símbolo R$. Débito é armazenado "
                    "como positivo e crédito como negativo."
                ),
                max_digits=14,
                null=True,
                verbose_name="Valor",
            ),
        ),
        migrations.AddConstraint(
            model_name="newrelease",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(value__isnull=True)
                    | models.Q(launchType="D", value__gt=0)
                    | models.Q(launchType="C", value__lt=0)
                ),
                name="ck_newrelease_value_sign_matches_launch_type",
                violation_error_message=(
                    "O valor deve ser positivo para débito e negativo para "
                    "crédito."
                ),
            ),
        ),
    ]
