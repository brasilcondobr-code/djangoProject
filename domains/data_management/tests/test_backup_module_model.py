import datetime

import pytest
from django.db import IntegrityError, transaction

from domains.data_management.models import BackupModule

pytestmark = pytest.mark.django_db


class TestBackupModuleModel:

    def test_create_backup_defaults(self):
        backup = BackupModule.objects.create(
            title='Backup Teste',
            dateTime=datetime.date(2026, 9, 7),
        )
        assert backup.pk is not None
        assert backup.title == 'Backup Teste'
        assert backup.status == BackupModule.Status.PENDING
        assert backup.get_status_display() == 'Pendente'
        assert backup.is_active is True
        assert backup.file_url == ''
        assert backup.description is None
        assert backup.created_at is not None
        assert backup.updated_at is not None

    def test_required_fields(self):
        with pytest.raises(Exception):
            BackupModule.objects.create(title='Sem data')

        with pytest.raises(Exception):
            BackupModule.objects.create(dateTime=datetime.date(2026, 9, 7))

    def test_max_lengths(self):
        assert BackupModule._meta.get_field('title').max_length == 250
        assert BackupModule._meta.get_field('status').max_length == 50
        assert BackupModule._meta.get_field('file_url').max_length == 255

    def test_field_requirements(self):
        from django.db import models

        title = BackupModule._meta.get_field('title')
        assert title.blank is False
        assert title.null is False
        date_time = BackupModule._meta.get_field('dateTime')
        assert isinstance(date_time, models.DateField)
        assert date_time.blank is False
        file_url = BackupModule._meta.get_field('file_url')
        assert file_url.null is False
        assert file_url.default == ''
        assert file_url.blank is True

    def test_verbose_names(self):
        assert BackupModule._meta.verbose_name == '01. Backup'
        assert BackupModule._meta.verbose_name_plural == '01. Backups'
        assert BackupModule._meta.app_label == 'data_management'
        assert BackupModule._meta.get_field('title').verbose_name == 'Título'
        assert BackupModule._meta.get_field('file_url').verbose_name == 'Arquivo de Backup'

    def test_str_returns_title(self):
        backup = BackupModule.objects.create(
            title='Backup do Mês', dateTime=datetime.date(2026, 9, 7)
        )
        assert str(backup) == 'Backup do Mês'

    def test_unique_constraint_exists(self):
        unique = next(
            (c for c in BackupModule._meta.constraints if c.name == 'unique_backup_title_datetime'),
            None,
        )
        assert unique is not None
        assert unique.fields == ('title', 'dateTime')

    def test_database_enforces_unique_title_datetime(self):
        BackupModule.objects.create(
            title='Backup Único', dateTime=datetime.date(2026, 9, 7)
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                BackupModule.objects.create(
                    title='Backup Único', dateTime=datetime.date(2026, 9, 7)
                )

    def test_same_title_different_date_allowed(self):
        BackupModule.objects.create(
            title='Backup Único', dateTime=datetime.date(2026, 9, 7)
        )
        other = BackupModule.objects.create(
            title='Backup Único', dateTime=datetime.date(2026, 9, 8)
        )
        assert other.pk is not None

    def test_status_choices(self):
        values = [value for value, _ in BackupModule.Status.choices]
        assert values == [
            BackupModule.Status.PENDING,
            BackupModule.Status.RUNNING,
            BackupModule.Status.DONE,
            BackupModule.Status.FAILED,
            BackupModule.Status.INACTIVE,
            BackupModule.Status.RESTORING,
        ]
