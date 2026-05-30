from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='TypesCondominium',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255, unique=True, verbose_name='Tipo de Condomínio')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                        ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                        ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                    ],
                    options={
                        'verbose_name': '1. Tipo de Condomínio',
                        'verbose_name_plural': '1. Tipos de Condomínios',
                        'ordering': ['name', 'is_active', 'created_at'],
                        'unique_together': {('name',)},
                        'db_table': 'condominium_typescondominium',
                    },
                ),
                migrations.CreateModel(
                    name='StructionCondominium',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255, unique=True, verbose_name='Estrutura do Condomínio')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                        ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                        ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                    ],
                    options={
                        'verbose_name': '2. Estrutura do Condomínio',
                        'verbose_name_plural': '2. Estruturas dos Condomínios',
                        'ordering': ['name', 'is_active', 'created_at'],
                        'unique_together': {('name',)},
                        'db_table': 'condominium_structioncondominium',
                    },
                ),
                migrations.CreateModel(
                    name='States',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=100, unique=True, verbose_name='Estado')),
                        ('abbreviation', models.CharField(max_length=2, unique=True, verbose_name='UF')),
                        ('capital', models.CharField(max_length=100, verbose_name='Capital', null=True, blank=False)),
                        ('region', models.CharField(choices=[('Região Norte', 'Região Norte'), ('Região Nordeste', 'Região Nordeste'), ('Região Centro-Oeste', 'Região Centro-Oeste'), ('Região Sudeste', 'Região Sudeste'), ('Região Sul', 'Região Sul')], max_length=100, null=True, verbose_name='Região')),
                        ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                        ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                    ],
                    options={
                        'verbose_name': '3. Estado',
                        'verbose_name_plural': '3. Estados',
                        'ordering': ['abbreviation', 'name', 'region'],
                        'unique_together': {('name', 'abbreviation')},
                        'db_table': 'condominium_states',
                    },
                ),
                migrations.CreateModel(
                    name='Addresses',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                        ('street', models.CharField(max_length=255, verbose_name='Logradouro')),
                        ('number', models.IntegerField(verbose_name='Número')),
                        ('complement', models.CharField(blank=True, max_length=255, null=False, verbose_name='Complemento')),
                        ('neighborhood', models.CharField(blank=True, max_length=255, null=True, verbose_name='Bairro')),
                        ('city', models.CharField(max_length=100, verbose_name='Município')),
                        ('country', models.CharField(default='Brasil', max_length=100, verbose_name='País')),
                        ('zip_code', models.CharField(max_length=20, verbose_name='CEP')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('state', models.ForeignKey(on_delete=models.CASCADE, related_name='address', to='parameters.states', verbose_name='UF')),
                    ],
                    options={
                        'verbose_name': '4. Endereço',
                        'verbose_name_plural': '4. Endereços',
                        'ordering': ['country', 'state', 'city', 'street', 'number', 'complement', 'is_active', 'created_at'],
                        'unique_together': {('street', 'number', 'neighborhood', 'city', 'state', 'zip_code')},
                        'db_table': 'condominium_addresses',
                    },
                ),
            ],
        ),
    ]
