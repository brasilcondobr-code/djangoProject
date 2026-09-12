import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            'condominium',
            '0038_alter_collaborator_name_alter_condominium_is_active_and_more',
        ),
        ('data_management', '0011_alter_scheduledtaskmodule_virtual_meeting'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportmodule',
            name='condominium',
            field=models.ForeignKey(
                help_text='Condomínio dono desta configuração de exportação',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='exports',
                to='condominium.condominium',
                verbose_name='Condomínio',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='group',
            field=models.CharField(
                help_text='Grupo do módulo, ex.: parameters',
                max_length=250,
                verbose_name='Grupo',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='module',
            field=models.CharField(
                help_text='Módulo a exportar, ex.: condominium_types',
                max_length=250,
                verbose_name='Módulo',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='file_format',
            field=models.CharField(
                choices=[('csv', 'CSV'), ('xlsx', 'XLSX')],
                default='csv',
                help_text='CSV ou XLSX',
                max_length=10,
                verbose_name='Formato do arquivo',
            ),
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='export_service',
            field=models.CharField(
                help_text='Chave do serviço registrado no código, ex.: '
                          'parameters.condominium_types',
                max_length=255,
                verbose_name='Serviço de exportação',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='description',
            field=models.TextField(
                blank=True,
                help_text='Descrição opcional da exportação',
                verbose_name='Descrição',
            ),
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Indica se o registro está ativo',
                verbose_name='Ativo',
            ),
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='generate_datetime',
            field=models.DateTimeField(
                blank=True,
                editable=False,
                help_text='Preenchido automaticamente quando o arquivo é gerado',
                null=True,
                verbose_name='Data/hora da geração',
            ),
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='file_generate',
            field=models.CharField(
                blank=True,
                default='',
                editable=False,
                help_text='Nome do arquivo gerado (somente leitura)',
                max_length=250,
                verbose_name='Arquivo gerado',
            ),
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='file_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pendente'),
                    ('queued', 'Na fila'),
                    ('processing', 'Processando'),
                    ('completed', 'Concluído'),
                    ('failed', 'Falha'),
                    ('cancelled', 'Cancelado'),
                ],
                default='pending',
                editable=False,
                help_text='Status da exportação (somente leitura)',
                max_length=20,
                verbose_name='Status do arquivo',
            ),
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Criado em'),
        ),
        migrations.AddField(
            model_name='exportmodule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Atualizado em'),
        ),
        migrations.AlterModelOptions(
            name='exportmodule',
            options={
                'ordering': ['-updated_at'],
                'verbose_name': '02. Exportação',
                'verbose_name_plural': '02. Exportações',
            },
        ),
        migrations.AddConstraint(
            model_name='exportmodule',
            constraint=models.UniqueConstraint(
                fields=('condominium', 'group', 'module', 'file_format'),
                name='unique_export_configuration',
            ),
        ),
        migrations.AddIndex(
            model_name='exportmodule',
            index=models.Index(
                fields=['file_status', 'updated_at'],
                name='idx_export_status_updated',
            ),
        ),
    ]