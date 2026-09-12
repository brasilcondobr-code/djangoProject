import pytest
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from domains.administrative.models.task import Task
from domains.administrative.services.tasks_service import TaskService


@pytest.mark.django_db
class TestTaskService:

    @pytest.fixture
    def _user(self):
        return User.objects.create_user(username='testuser', password='12345')

    def _valid_data(self, _condo):
        return {
            'condominium': _condo,
            'title': 'Tarefa de serviço',
            'release_date': date(2026, 1, 15),
            'estimated_completion_date': date(2026, 2, 15),
            'description': 'Descrição da tarefa',
        }

    def test_create_task(self, _condo, _user):
        task = TaskService.create_task(_user, self._valid_data(_condo))
        assert task.pk is not None
        assert task.title == 'Tarefa de serviço'

    def test_update_task(self, _condo, _user):
        data = self._valid_data(_condo)
        data['created_by_user'] = _user
        task = Task.objects.create(**data)
        TaskService.update_task(_user, task, {'title': 'Título atualizado'})
        task.refresh_from_db()
        assert task.title == 'Título atualizado'

    def test_update_task_denied_for_non_creator(self, _condo, _user):
        from django.contrib.auth.models import User
        from django.core.exceptions import PermissionDenied

        other = User.objects.create_user(username='otheruser', password='12345')
        task = Task.objects.create(
            **self._valid_data(_condo),
            created_by_user=other,
        )
        with pytest.raises(PermissionDenied):
            TaskService.update_task(_user, task, {'title': 'Tentativa'})

    def test_validate_dates_valid(self):
        TaskService.validate_task_dates(
            release_date=date(2026, 1, 1),
            estimated_completion_date=date(2026, 1, 31),
            completion_date=date(2026, 1, 30),
        )

    def test_validate_dates_estimated_before_release(self):
        with pytest.raises(ValidationError):
            TaskService.validate_task_dates(
                release_date=date(2026, 2, 1),
                estimated_completion_date=date(2026, 1, 31),
            )

    def test_validate_dates_completion_before_release(self):
        with pytest.raises(ValidationError):
            TaskService.validate_task_dates(
                release_date=date(2026, 2, 1),
                estimated_completion_date=date(2026, 3, 1),
                completion_date=date(2026, 1, 1),
            )

    def test_validate_description_valid(self):
        TaskService.validate_description('<p>Descrição válida</p>')

    def test_validate_description_empty(self):
        with pytest.raises(ValidationError):
            TaskService.validate_description('<p></p>')

    def test_get_admin_queryset(self, _condo):
        Task.objects.create(**self._valid_data(_condo))
        qs = TaskService.get_admin_queryset()
        assert qs.count() == 1
