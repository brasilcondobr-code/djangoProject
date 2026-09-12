import pytest
from domains.parameters.models.assembly_status import AssemblyStatus
from domains.parameters.services.assembly_status_service import AssemblyStatusService


@pytest.mark.django_db
class TestAssemblyStatusService:

    def test_create_with_success(self):
        status = AssemblyStatusService.create_assembly_status({
            'description': ' Está em execução ',
            'is_pending': False,
            'is_running': True,
        })
        assert status.pk is not None
        assert status.description == 'Está em execução'
        assert status.is_running is True

    def test_update_with_success(self):
        status = AssemblyStatus.objects.create(description='Status original')
        updated = AssemblyStatusService.update_assembly_status(
            status, {'description': 'Status atualizado'}
        )
        updated.refresh_from_db()
        assert updated.description == 'Status atualizado'

    def test_delete_with_success(self):
        status = AssemblyStatus.objects.create(description='Status a remover')
        AssemblyStatusService.delete_assembly_status(status)
        assert not AssemblyStatus.objects.filter(pk=status.pk).exists()

    def test_create_rejects_empty_description(self):
        with pytest.raises(ValueError):
            AssemblyStatusService.create_assembly_status({'description': '   '})

    def test_create_fails_on_duplicate_description(self):
        AssemblyStatusService.create_assembly_status({'description': 'Pendente'})
        with pytest.raises(ValueError) as exc_info:
            AssemblyStatusService.create_assembly_status({'description': ' pendente '})
        assert 'descrição' in str(exc_info.value)

    def test_update_fails_on_duplicate_description(self):
        AssemblyStatusService.create_assembly_status({'description': 'Em execucao'})
        other = AssemblyStatusService.create_assembly_status({'description': 'Outra'})
        with pytest.raises(ValueError):
            AssemblyStatusService.update_assembly_status(other, {'description': 'EM EXECUCAO'})

    def test_create_second_running_fails(self):
        AssemblyStatusService.create_assembly_status({
            'description': 'Execução 1', 'is_running': True, 'is_pending': False
        })
        with pytest.raises(ValueError) as exc_info:
            AssemblyStatusService.create_assembly_status({
                'description': 'Execução 2', 'is_running': True, 'is_pending': False
            })
        assert 'Em execução' in str(exc_info.value)

    def test_create_second_complete_fails(self):
        AssemblyStatusService.create_assembly_status({
            'description': 'Concluída 1', 'is_complete': True, 'is_pending': False
        })
        with pytest.raises(ValueError) as exc_info:
            AssemblyStatusService.create_assembly_status({
                'description': 'Concluída 2', 'is_complete': True, 'is_pending': False
            })
        assert 'Completo' in str(exc_info.value)

    def test_update_second_running_fails(self):
        AssemblyStatusService.create_assembly_status({
            'description': 'Execução', 'is_running': True, 'is_pending': False
        })
        other = AssemblyStatusService.create_assembly_status({'description': 'Livro'})
        with pytest.raises(ValueError):
            AssemblyStatusService.update_assembly_status(
                other, {'is_running': True, 'is_pending': False}
            )

    def test_toggle_active(self):
        status = AssemblyStatusService.create_assembly_status({'description': 'Pendente'})
        AssemblyStatusService.toggle_active(status, False)
        status.refresh_from_db()
        assert status.is_active is False

    def test_normalization_applied(self):
        data = {
            'description': '  Concluída  ',
            'is_complete': True,
            'is_pending': False,
        }
        status = AssemblyStatusService.create_assembly_status(data)
        assert status.description == 'Concluída'

    def test_db_constraint_is_final_guard_for_running(self):
        from django.db import IntegrityError
        AssemblyStatusService.create_assembly_status({
            'description': 'Em execução', 'is_running': True, 'is_pending': False
        })
        with pytest.raises(IntegrityError):
            AssemblyStatus.objects.create(
                description='Fora do service',
                is_running=True,
                is_pending=False,
            )