from django.db import migrations, models


def gen_default_account_type(apps, schema_editor):
    Accountingclasstypes = apps.get_model('parameters', 'Accountingclasstypes')
    Chartofaccountstype = apps.get_model('parameters', 'Chartofaccountstype')
    if not Accountingclasstypes.objects.exists():
        return
    default_type = Chartofaccountstype.objects.first()
    if not default_type:
        default_type = Chartofaccountstype.objects.create(
            code='T001',
            description='Tipo padrão',
            nature='devedora',
        )
    Accountingclasstypes.objects.update(account_type=default_type)


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0019_chartofaccountsmaingroup_account_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountingclasstypes',
            name='nature',
        ),
        migrations.AddField(
            model_name='accountingclasstypes',
            name='account_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='accounting_classes', to='parameters.chartofaccountstype', verbose_name='Tipo de conta contábil'),
        ),
        migrations.RunPython(gen_default_account_type, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='accountingclasstypes',
            name='account_type',
            field=models.ForeignKey(on_delete=models.PROTECT, related_name='accounting_classes', to='parameters.chartofaccountstype', verbose_name='Tipo de conta contábil'),
            preserve_default=False,
        ),
    ]
