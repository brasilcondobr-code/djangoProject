from django.db import migrations, models


def gen_unique_codes(apps, schema_editor):
    Chartofaccountstype = apps.get_model('parameters', 'Chartofaccountstype')
    for i, obj in enumerate(Chartofaccountstype.objects.iterator(), start=1):
        obj.code = f'T{i:03d}'
        obj.save(update_fields=['code'])


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0017_accountingclasstypes_code_nature'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartofaccountstype',
            name='nature',
            field=models.CharField(default='devedora', max_length=50, verbose_name='Natureza contábil'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chartofaccountstype',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Código do tipo'),
        ),
        migrations.RunPython(gen_unique_codes, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chartofaccountstype',
            name='code',
            field=models.CharField(max_length=50, unique=True, verbose_name='Código do tipo'),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='chartofaccountstype',
            options={'ordering': ['code'], 'verbose_name': '17. Tipo de Conta Contábil', 'verbose_name_plural': '17. Tipos de Contas Contábeis'},
        ),
    ]
