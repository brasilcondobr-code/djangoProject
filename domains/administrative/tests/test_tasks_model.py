import pytest
from django.db import IntegrityError
from django.contrib.auth.models import User
from domains.administrative.models.task import Task
from domains.condominium.models import Condominium
from domains.email_service.models import ConnectionStatus


@pytest.mark.django_db
class TestTaskModel:

    @pytest.fixture
    def _user(self):
        return User.objects.create_user(username='testuser', password='12345')

    def test_create_task_minimal(self, _condo):
        task = Task.objects.create(
            condominium=_condo,
            title='Manutenção elevador',
            release_date='2026-01-15',
            estimated_completion_date='2026-02-15',
            description='Descrição da tarefa',
        )
        assert task.pk is not None
        assert task.title == 'Manutenção elevador'
        assert task.is_active is True
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_with_all_fields(self, _condo, _user):
        status = ConnectionStatus.objects.create(status='Pendente')
        task = Task.objects.create(
            condominium=_condo,
            created_by_user=_user,
            responsible_user=_user,
            title='Tarefa completa',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            completion_date='2026-01-30',
            description='Descrição detalhada',
            is_active=True,
            status=status,
        )
        assert task.created_by_user == _user
        assert task.responsible_user == _user
        assert task.completion_date is not None

    def test_title_unique_per_condominium(self, _condo):
        Task.objects.create(
            condominium=_condo,
            title='Título único',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        with pytest.raises(IntegrityError):
            Task.objects.create(
                condominium=_condo,
                title='Título único',
                release_date='2026-02-01',
                estimated_completion_date='2026-02-28',
                description='Outra descrição',
            )

    def test_same_title_different_condominium(self, _condo, _address, _type_condo):
        condo2 = Condominium.objects.create(
            code='COND002', name='Outro Condomínio',
            cnpj='99.888.777/0001-66',
            state_registration='1', municipal_registration='1',
            type_condominium=_type_condo, address=_address,
        )
        Task.objects.create(
            condominium=_condo,
            title='Mesmo título',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        Task.objects.create(
            condominium=condo2,
            title='Mesmo título',
            release_date='2026-02-01',
            estimated_completion_date='2026-02-28',
            description='Outra descrição',
        )
        assert Task.objects.count() == 2

    def test_default_is_active(self, _condo):
        task = Task.objects.create(
            condominium=_condo,
            title='Ativo por padrão',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        assert task.is_active is True

    def test_str_returns_title(self, _condo):
        task = Task.objects.create(
            condominium=_condo,
            title='Minha Tarefa',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        assert str(task) == 'Minha Tarefa'

    def test_created_at_auto_set(self, _condo):
        task = Task.objects.create(
            condominium=_condo,
            title='Timestamps',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        assert task.created_at is not None

    def test_updated_at_changes_on_update(self, _condo):
        task = Task.objects.create(
            condominium=_condo,
            title='Atualização',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        original_updated = task.updated_at
        task.title = 'Atualizado'
        task.save()
        task.refresh_from_db()
        assert task.updated_at >= original_updated

    def test_condominium_relation(self, _condo):
        task = Task.objects.create(
            condominium=_condo,
            title='Relacionamento',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        assert task.condominium == _condo
        assert _condo.tasks.count() == 1
