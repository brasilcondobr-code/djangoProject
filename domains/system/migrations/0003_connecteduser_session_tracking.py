from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("system", "0002_delete_emailconfiguration_delete_smsconfiguration_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="connecteduser",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="connected_user_sessions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usuário",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="session_key",
            field=models.CharField(
                blank=True,
                max_length=40,
                null=True,
                unique=True,
                verbose_name="Chave da sessão",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="connected_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Conectado em",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="last_activity",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Última atividade",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="disconnected_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Desconectado em",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="is_connected",
            field=models.BooleanField(default=True, verbose_name="Conectado"),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="ip_address",
            field=models.GenericIPAddressField(
                blank=True,
                null=True,
                verbose_name="Endereço IP",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="user_agent",
            field=models.CharField(
                blank=True,
                max_length=512,
                verbose_name="Navegador",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="created_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Criado em",
            ),
        ),
        migrations.AddField(
            model_name="connecteduser",
            name="updated_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Atualizado em",
            ),
        ),
        migrations.AlterField(
            model_name="connecteduser",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="connected_user_sessions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usuário",
            ),
        ),
        migrations.AlterField(
            model_name="connecteduser",
            name="session_key",
            field=models.CharField(
                max_length=40,
                unique=True,
                verbose_name="Chave da sessão",
            ),
        ),
        migrations.AlterField(
            model_name="connecteduser",
            name="connected_at",
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name="Conectado em",
            ),
        ),
        migrations.AlterField(
            model_name="connecteduser",
            name="last_activity",
            field=models.DateTimeField(verbose_name="Última atividade"),
        ),
        migrations.AlterField(
            model_name="connecteduser",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name="Criado em",
            ),
        ),
        migrations.AlterField(
            model_name="connecteduser",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                verbose_name="Atualizado em",
            ),
        ),
        migrations.AddIndex(
            model_name="connecteduser",
            index=models.Index(
                fields=("is_connected", "last_activity"),
                name="system_conn_is_conn_3f0c8a_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="connecteduser",
            index=models.Index(
                fields=("user", "is_connected"),
                name="system_conn_user_id_1b7d24_idx",
            ),
        ),
    ]
