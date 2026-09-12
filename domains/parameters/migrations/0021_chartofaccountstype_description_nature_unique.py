from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0020_accountingclasstypes_remove_nature_add_account_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chartofaccountstype',
            name='description',
            field=models.CharField(max_length=100, verbose_name='Descrição'),
        ),
        migrations.AlterField(
            model_name='chartofaccountstype',
            name='nature',
            field=models.CharField(choices=[('devedora', 'Devedora'), ('credora', 'Credora')], max_length=50, verbose_name='Natureza contábil'),
        ),
        migrations.AddConstraint(
            model_name='chartofaccountstype',
            constraint=models.UniqueConstraint(fields=('description', 'nature'), name='uq_chartofaccountstype_description_nature'),
        ),
    ]
