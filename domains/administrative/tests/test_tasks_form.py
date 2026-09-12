import pytest
from datetime import date
from django.contrib.auth.models import User
from domains.administrative.forms.tasks_form import TaskForm
from domains.administrative.models.task import Task
from domains.email_service.models import ConnectionStatus


@pytest.mark.django_db
class TestTaskForm:

    def _valid_data(self, _condo, **overrides):
        data = {
            'condominium': _condo.pk,
            'title': 'Tarefa de teste',
            'release_date': '2026-01-15',
            'estimated_completion_date': '2026-02-15',
            'description': '<p>Descrição válida</p>',
            'is_active': True,
        }
        data.update(overrides)
        return data

    def test_form_valid(self, _condo):
        form = TaskForm(data=self._valid_data(_condo))
        assert form.is_valid(), form.errors

    def test_condominium_required(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, condominium=''))
        assert not form.is_valid()
        assert 'condominium' in form.errors

    def test_title_required(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, title=''))
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_title_blank_spaces(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, title='   '))
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_title_max_length(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, title='X' * 256))
        assert not form.is_valid()

    def test_title_unique_per_condominium(self, _condo):
        Task.objects.create(
            condominium=_condo,
            title='Título existente',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        form = TaskForm(data=self._valid_data(_condo, title='Título existente'))
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_same_title_different_condo_allowed(self, _condo, _address, _type_condo):
        from domains.condominium.models import Condominium
        condo2 = Condominium.objects.create(
            code='COND002', name='Outro Condomínio',
            cnpj='99.888.777/0001-66',
            state_registration='1', municipal_registration='1',
            type_condominium=_type_condo, address=_address,
        )
        Task.objects.create(
            condominium=_condo,
            title='Título compartilhado',
            release_date='2026-01-01',
            estimated_completion_date='2026-01-31',
            description='Descrição',
        )
        form = TaskForm(data=self._valid_data(condo2, title='Título compartilhado', condominium=condo2.pk))
        assert form.is_valid(), form.errors

    def test_release_date_required(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, release_date=''))
        assert not form.is_valid()
        assert 'release_date' in form.errors

    def test_estimated_completion_date_required(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, estimated_completion_date=''))
        assert not form.is_valid()
        assert 'estimated_completion_date' in form.errors

    def test_completion_date_optional(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, completion_date=''))
        assert form.is_valid(), form.errors

    def test_completion_date_before_release(self, _condo):
        form = TaskForm(data=self._valid_data(
            _condo,
            release_date='2026-02-01',
            completion_date='2026-01-01',
        ))
        assert not form.is_valid()
        assert 'completion_date' in form.errors

    def test_estimated_date_before_release(self, _condo):
        form = TaskForm(data=self._valid_data(
            _condo,
            release_date='2026-02-01',
            estimated_completion_date='2026-01-01',
        ))
        assert not form.is_valid()
        assert 'estimated_completion_date' in form.errors

    def test_description_required(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, description=''))
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_empty_html(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, description='<p></p>'))
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_whitespace_html(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, description='<p>&nbsp;</p>'))
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_block_scripts(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, description='<script>alert("xss")</script>'))
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_is_active_default_true(self, _condo):
        form = TaskForm(data=self._valid_data(_condo))
        assert form.is_valid(), form.errors
        assert form.cleaned_data['is_active'] is True

    def test_status_optional(self, _condo):
        form = TaskForm(data=self._valid_data(_condo))
        assert form.is_valid(), form.errors
        assert form.cleaned_data.get('status') is None

    def test_created_by_user_readonly_and_empty(self, _condo):
        form = TaskForm(data=self._valid_data(_condo))
        assert form.is_valid(), form.errors
        assert form.cleaned_data.get('created_by_user') is None

    def test_status_default_pendente_on_create(self, _condo):
        status = ConnectionStatus.objects.create(status='Pendente')
        form = TaskForm(data=self._valid_data(_condo))
        assert form.is_valid(), form.errors

    def test_clean_title_strips_whitespace(self, _condo):
        form = TaskForm(data=self._valid_data(_condo, title='  Meu título  '))
        assert form.is_valid(), form.errors
        assert form.cleaned_data['title'] == 'Meu título'
