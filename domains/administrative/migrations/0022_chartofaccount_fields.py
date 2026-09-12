import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrative', '0021_bank_and_bankaccount_refinements'),
        ('parameters', '0016_chartofaccounts_models'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='ChartOfAccount',
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="DROP TABLE IF EXISTS administrative_chartofaccount",
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
        migrations.CreateModel(
            name='ChartOfAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_code', models.CharField(max_length=20, verbose_name='Código da conta')),
                ('account_name', models.CharField(max_length=150, verbose_name='Nome da conta')),
                ('account_level', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Nível hierárquico')),
                ('account_description', models.TextField(blank=True, max_length=1000, verbose_name='Descrição detalhada da conta')),
                ('external_reference', models.CharField(blank=True, max_length=50, verbose_name='Referência externa')),
                ('effective_start_date', models.DateField(verbose_name='Data inicial de vigência')),
                ('effective_end_date', models.DateField(blank=True, null=True, verbose_name='Data final de vigência')),
                ('is_default', models.BooleanField(default=False, verbose_name='Conta padrão')),
                ('is_system_account', models.BooleanField(default=False, verbose_name='Conta do sistema')),
                ('can_be_archived', models.BooleanField(default=True, verbose_name='Permite arquivamento')),
                ('archive_reason', models.CharField(blank=True, max_length=255, verbose_name='Motivo do arquivamento')),
                ('version', models.CharField(blank=True, default='1.0', max_length=20, verbose_name='Versão do cadastro')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='Aprovado em')),
                ('change_reason', models.CharField(blank=True, max_length=500, verbose_name='Motivo da alteração')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='approved_chart_of_accounts', to='condominium.collaborator', verbose_name='Aprovado por')),
                ('account_class', models.ForeignKey(on_delete=models.PROTECT, related_name='chart_of_accounts', to='parameters.accountingclasstypes', verbose_name='Classe contábil')),
                ('account_group', models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='chart_of_accounts', to='parameters.chartofaccountsmaingroup', verbose_name='Grupo principal')),
                ('account_subgroup', models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='chart_of_accounts', to='parameters.chartofaccountssubgroup', verbose_name='Subgrupo')),
                ('account_type', models.ForeignKey(on_delete=models.PROTECT, related_name='chart_of_accounts', to='parameters.chartofaccountstype', verbose_name='Tipo da conta')),
                ('condominium', models.ForeignKey(on_delete=models.CASCADE, related_name='chart_of_accounts', to='condominium.condominium', verbose_name='Condomínio')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='created_chart_of_accounts', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('parent_account', models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='child_accounts', to='self', verbose_name='Conta-pai')),
                ('replacement_account', models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='accounts_replaced', to='self', verbose_name='Conta substituta')),
                ('status', models.ForeignKey(on_delete=models.PROTECT, related_name='chart_of_accounts', to='parameters.chartofaccountsstatus', verbose_name='Situação da conta')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, related_name='updated_chart_of_accounts', to=settings.AUTH_USER_MODEL, verbose_name='Atualizado por')),
            ],
            options={
                'verbose_name': '09. Plano de Conta',
                'verbose_name_plural': '09. Plano de Contas',
                'ordering': ['condominium', 'account_code'],
                'db_table': 'administrative_chartofaccount',
            },
        ),
        migrations.AddConstraint(
            model_name='chartofaccount',
            constraint=models.UniqueConstraint(fields=('condominium', 'account_code'), name='uq_chart_account_condominium_code'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['condominium', 'account_code'], name='administrat_condomi_0f5430_idx'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['condominium', 'status'], name='administrat_condomi_06f3f3_idx'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['condominium', 'account_level'], name='administrat_condomi_cb76f2_idx'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['condominium', 'parent_account'], name='administrat_condomi_ec7037_idx'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['account_code'], name='administrat_account_94b8ac_idx'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['account_name'], name='administrat_account_20c0cf_idx'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['effective_start_date'], name='administrat_effecti_8a803a_idx'),
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['effective_end_date'], name='administrat_effecti_26a54b_idx'),
        ),
    ]
