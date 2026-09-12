import pytest
from django.db import IntegrityError
from domains.parameters.models.assembly_status import AssemblyStatus


@pytest.mark.django_db
class TestAssemblyStatusModel:

    def test_create_with_defaults(self):
        status = AssemblyStatus.objects.create(description='Pendente')
        assert status.pk is not None
        assert status.is_pending is True
        assert status.is_running is False
        assert status.is_complete is False
        assert status.is_active is True

    def test_create_with_boolean_flags(self):
        status = AssemblyStatus.objects.create(
            description='Em execução',
            is_pending=False,
            is_running=True,
        )
        status.refresh_from_db()
        assert status.is_running is True
        assert status.is_pending is False

    def test_description_required(self):
        with pytest.raises(IntegrityError):
            AssemblyStatus.objects.create(description=None)

    def test_description_max_length(self):
        field = AssemblyStatus._meta.get_field('description')
        assert field.max_length == 255

    def test_description_unique(self):
        AssemblyStatus.objects.create(description='Concluída')
        with pytest.raises(IntegrityError):
            AssemblyStatus.objects.create(description='Concluída')

    def test_str_returns_description(self):
        status = AssemblyStatus.objects.create(description='Cancelada')
        assert str(status) == 'Cancelada'

    def test_multiple_records_can_be_pending(self):
        first = AssemblyStatus.objects.create(description='Pendente 1')
        second = AssemblyStatus.objects.create(description='Pendente 2')
        assert first.is_pending and second.is_pending

    def test_only_one_running_allowed(self):
        AssemblyStatus.objects.create(
            description='Em execução', is_running=True, is_pending=False
        )
        with pytest.raises(IntegrityError):
            AssemblyStatus.objects.create(
                description='Segunda em execução', is_running=True, is_pending=False
            )

    def test_only_one_complete_allowed(self):
        AssemblyStatus.objects.create(
            description='Concluída', is_complete=True, is_pending=False
        )
        with pytest.raises(IntegrityError):
            AssemblyStatus.objects.create(
                description='Segunda concluída', is_complete=True, is_pending=False
            )

    def test_update_running_second_conflicts(self):
        first = AssemblyStatus.objects.create(
            description='Em execução', is_running=True, is_pending=False
        )
        second = AssemblyStatus.objects.create(description='Outro status')
        second.is_running = True
        second.is_pending = False
        with pytest.raises(IntegrityError):
            second.save()

    def test_update_complete_second_conflicts(self):
        first = AssemblyStatus.objects.create(
            description='Concluída', is_complete=True, is_pending=False
        )
        second = AssemblyStatus.objects.create(description='Outro status')
        second.is_complete = True
        second.is_pending = False
        with pytest.raises(IntegrityError):
            second.save()

    def test_updated_at_changes_on_update(self):
        status = AssemblyStatus.objects.create(description='Status Original')
        original_updated = status.updated_at
        status.description = 'Status Atualizado'
        status.save()
        status.refresh_from_db()
        assert status.updated_at >= original_updated

    def test_created_at_auto_set(self):
        status = AssemblyStatus.objects.create(description='Status novo')
        assert status.created_at is not None

    def test_verbose_names(self):
        assert AssemblyStatus._meta.verbose_name == '23. Status da Assembleia'
        assert AssemblyStatus._meta.verbose_name_plural == '23. Status das Assembleias'

    def test_running_constraint_exists(self):
        names = [c.name for c in AssemblyStatus._meta.constraints]
        assert 'unique_running_assembly_status' in names
        assert 'unique_complete_assembly_status' in names