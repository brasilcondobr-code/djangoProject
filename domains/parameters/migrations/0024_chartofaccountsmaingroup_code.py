from django.db import migrations, models


def gen_unique_codes(apps, schema_editor):
    ChartofaccountsMaingroup = apps.get_model('parameters', 'ChartofaccountsMaingroup')
    for i, obj in enumerate(ChartofaccountsMaingroup.objects.iterator(), start=1):
        obj.code = f'MG{i:03d}'
        obj.save(update_fields=['code'])


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0023_chartofaccountssubgroup_main_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartofaccountsmaingroup',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Código'),
        ),
        migrations.RunPython(gen_unique_codes, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chartofaccountsmaingroup',
            name='code',
            field=models.CharField(max_length=50, unique=True, verbose_name='Código'),
            preserve_default=False,
        ),
    ]
