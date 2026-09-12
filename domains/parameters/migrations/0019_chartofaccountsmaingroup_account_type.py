from django.db import migrations, models


def gen_default_account_type(apps, schema_editor):
    ChartofaccountsMaingroup = apps.get_model('parameters', 'ChartofaccountsMaingroup')
    Chartofaccountstype = apps.get_model('parameters', 'Chartofaccountstype')
    if not ChartofaccountsMaingroup.objects.exists():
        return
    default_type = Chartofaccountstype.objects.first()
    if not default_type:
        default_type = Chartofaccountstype.objects.create(
            code='T001',
            description='Tipo padrão',
            nature='devedora',
        )
    ChartofaccountsMaingroup.objects.update(account_type=default_type)


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0018_chartofaccountstype_code_nature'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartofaccountsmaingroup',
            name='account_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='main_groups', to='parameters.chartofaccountstype', verbose_name='Tipo de conta contábil'),
        ),
        migrations.RunPython(gen_default_account_type, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chartofaccountsmaingroup',
            name='account_type',
            field=models.ForeignKey(on_delete=models.PROTECT, related_name='main_groups', to='parameters.chartofaccountstype', verbose_name='Tipo de conta contábil'),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='chartofaccountsmaingroup',
            options={'ordering': ['account_type', 'description'], 'verbose_name': '19. Grupo Principal de Conta', 'verbose_name_plural': '19. Grupos Principais de Contas'},
        ),
    ]
