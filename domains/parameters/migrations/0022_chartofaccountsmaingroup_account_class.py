from django.db import migrations, models


def gen_default_account_class(apps, schema_editor):
    ChartofaccountsMaingroup = apps.get_model('parameters', 'ChartofaccountsMaingroup')
    Accountingclasstypes = apps.get_model('parameters', 'Accountingclasstypes')
    Chartofaccountstype = apps.get_model('parameters', 'Chartofaccountstype')
    if not ChartofaccountsMaingroup.objects.exists():
        return
    default_class = Accountingclasstypes.objects.first()
    if not default_class:
        default_type = Chartofaccountstype.objects.first()
        if not default_type:
            default_type = Chartofaccountstype.objects.create(
                code='T001', description='Tipo padrão', nature='devedora',
            )
        default_class = Accountingclasstypes.objects.create(
            code='C001', description='Classe padrão', account_type=default_type,
        )
    ChartofaccountsMaingroup.objects.update(account_class=default_class)


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0021_chartofaccountstype_description_nature_unique'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chartofaccountsmaingroup',
            name='account_type',
        ),
        migrations.AddField(
            model_name='chartofaccountsmaingroup',
            name='account_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='main_groups', to='parameters.accountingclasstypes', verbose_name='Classes Contábeis'),
        ),
        migrations.RunPython(gen_default_account_class, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chartofaccountsmaingroup',
            name='account_class',
            field=models.ForeignKey(on_delete=models.PROTECT, related_name='main_groups', to='parameters.accountingclasstypes', verbose_name='Classes Contábeis'),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='chartofaccountsmaingroup',
            options={'ordering': ['account_class', 'description'], 'verbose_name': '19. Grupo Principal de Conta', 'verbose_name_plural': '19. Grupos Principais de Contas'},
        ),
    ]
