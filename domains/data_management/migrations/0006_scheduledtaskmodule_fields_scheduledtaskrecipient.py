import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0005_logmodule_alter_auditmodule_options_and_more'),
        ('administrative', '0038_virtualmeetingemailschedule_and_more'),
        ('residents', '0048_alter_resident_options_alter_resident_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='virtual_meeting',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='scheduled_tasks',
                to='administrative.virtualmeeting',
                verbose_name='Votação Virtual',
            ),
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='task_type',
            field=models.CharField(
                choices=[
                    ('notice', 'Edital de Convocação'),
                    ('voting', 'Convocação para Votação'),
                ],
                default='notice',
                max_length=20,
                verbose_name='Tipo de e-mail',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='scheduled_at',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name='Agendado para',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pendente'),
                    ('processing', 'Processando'),
                    ('sent', 'Enviado'),
                    ('failed', 'Falhou'),
                    ('canceled', 'Cancelado'),
                ],
                default='pending',
                max_length=20,
                verbose_name='Status',
            ),
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='attempts',
            field=models.PositiveIntegerField(default=0, verbose_name='Tentativas'),
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Enviado em'),
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='last_error',
            field=models.TextField(blank=True, default='', verbose_name='Último erro'),
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='celery_task_id',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='ID da tarefa Celery'),
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Criado em',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scheduledtaskmodule',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='Atualizado em',
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ScheduledTaskRecipient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'email',
                    models.EmailField(max_length=254, verbose_name='E-mail'),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pendente'),
                            ('sent', 'Enviado'),
                            ('failed', 'Falhou'),
                            ('canceled', 'Cancelado'),
                        ],
                        default='pending',
                        max_length=20,
                        verbose_name='Status',
                    ),
                ),
                (
                    'sent_at',
                    models.DateTimeField(blank=True, null=True, verbose_name='Enviado em'),
                ),
                (
                    'last_error',
                    models.TextField(blank=True, default='', verbose_name='Último erro'),
                ),
                (
                    'created_at',
                    models.DateTimeField(auto_now_add=True, verbose_name='Criado em'),
                ),
                (
                    'updated_at',
                    models.DateTimeField(auto_now=True, verbose_name='Atualizado em'),
                ),
                (
                    'resident',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='scheduled_task_recipients',
                        to='residents.resident',
                        verbose_name='Morador',
                    ),
                ),
                (
                    'task',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='recipients',
                        to='data_management.scheduledtaskmodule',
                        verbose_name='Tarefa Agendada',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Destinatário de Tarefa Agendada',
                'verbose_name_plural': 'Destinatários de Tarefas Agendadas',
                'ordering': ['-created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.AddConstraint(
            model_name='scheduledtaskmodule',
            constraint=models.UniqueConstraint(
                fields=('virtual_meeting', 'task_type'),
                name='unique_scheduled_task_virtual_meeting_type',
            ),
        ),
        migrations.AddConstraint(
            model_name='scheduledtaskrecipient',
            constraint=models.UniqueConstraint(
                fields=('task', 'resident'),
                name='unique_scheduled_task_recipient',
            ),
        ),
    ]