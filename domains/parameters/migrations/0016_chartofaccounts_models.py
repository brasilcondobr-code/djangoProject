from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parameters', '0015_bankaccounttype_alter_assetbrand_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chartofaccountstype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100, unique=True, verbose_name='Descrição')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': '17. Tipo de Conta Contábil',
                'verbose_name_plural': '17. Tipos de Contas Contábeis',
                'ordering': ['description'],
                'db_table': 'parameters_chartofaccountstype',
            },
        ),
        migrations.CreateModel(
            name='Accountingclasstypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100, unique=True, verbose_name='Descrição')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': '18. Classe Contábil',
                'verbose_name_plural': '18. Classes Contábeis',
                'ordering': ['description'],
                'db_table': 'parameters_accountingclasstypes',
            },
        ),
        migrations.CreateModel(
            name='ChartofaccountsMaingroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100, unique=True, verbose_name='Descrição')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': '19. Grupo Principal de Conta',
                'verbose_name_plural': '19. Grupos Principais de Contas',
                'ordering': ['description'],
                'db_table': 'parameters_chartofaccountsmaingroup',
            },
        ),
        migrations.CreateModel(
            name='ChartofaccountsSubgroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100, unique=True, verbose_name='Descrição')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': '20. Subgrupo de Conta',
                'verbose_name_plural': '20. Subgrupos de Contas',
                'ordering': ['description'],
                'db_table': 'parameters_chartofaccountssubgroup',
            },
        ),
        migrations.CreateModel(
            name='ChartofaccountsStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50, unique=True, verbose_name='Descrição')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': '21. Situação de Conta Contábil',
                'verbose_name_plural': '21. Situações de Contas Contábeis',
                'ordering': ['description'],
                'db_table': 'parameters_chartofaccountsstatus',
            },
        ),
    ]
