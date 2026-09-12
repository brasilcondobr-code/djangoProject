from django.db import migrations, models


def gen_default_main_group(apps, schema_editor):
    ChartofaccountsSubgroup = apps.get_model('parameters', 'ChartofaccountsSubgroup')
    ChartofaccountsMaingroup = apps.get_model('parameters', 'ChartofaccountsMaingroup')
    Accountingclasstypes = apps.get_model('parameters', 'Accountingclasstypes')
    Chartofaccountstype = apps.get_model('parameters', 'Chartofaccountstype')
    if not ChartofaccountsSubgroup.objects.exists():
        return
    default_group = ChartofaccountsMaingroup.objects.first()
    if not default_group:
        default_type = Chartofaccountstype.objects.first()
        if not default_type:
            default_type = Chartofaccountstype.objects.create(
                code='T001', description='Tipo padrão', nature='devedora',
            )
        default_class = Accountingclasstypes.objects.first()
        if not default_class:
            default_class = Accountingclasstypes.objects.create(
                code='C001', description='Classe padrão', account_type=default_type,
            )
        default_group = ChartofaccountsMaingroup.objects.create(
            description='Grupo padrão', account_class=default_class,
        )
    ChartofaccountsSubgroup.objects.update(main_group=default_group)


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0022_chartofaccountsmaingroup_account_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartofaccountssubgroup',
            name='main_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='subgroups', to='parameters.chartofaccountsmaingroup', verbose_name='Grupos Principais de Contas Contábeis'),
        ),
        migrations.RunPython(gen_default_main_group, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chartofaccountssubgroup',
            name='main_group',
            field=models.ForeignKey(on_delete=models.PROTECT, related_name='subgroups', to='parameters.chartofaccountsmaingroup', verbose_name='Grupos Principais de Contas Contábeis'),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='chartofaccountssubgroup',
            options={'ordering': ['main_group', 'description'], 'verbose_name': '20. Subgrupo de Conta Contábil', 'verbose_name_plural': '20. Subgrupos de Contas Contábeis'},
        ),
    ]
