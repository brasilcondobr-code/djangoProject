from django.db import migrations, models


def gen_unique_codes(apps, schema_editor):
    ChartofaccountsSubgroup = apps.get_model('parameters', 'ChartofaccountsSubgroup')
    for i, obj in enumerate(ChartofaccountsSubgroup.objects.iterator(), start=1):
        obj.code = f'SG{i:03d}'
        obj.save(update_fields=['code'])


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0024_chartofaccountsmaingroup_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartofaccountssubgroup',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Código'),
        ),
        migrations.RunPython(gen_unique_codes, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chartofaccountssubgroup',
            name='code',
            field=models.CharField(max_length=50, unique=True, verbose_name='Código'),
            preserve_default=False,
        ),
    ]
