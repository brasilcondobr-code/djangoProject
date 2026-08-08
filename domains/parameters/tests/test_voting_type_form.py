import pytest
from django import forms as django_forms
from domains.parameters.forms import VotingTypeForm
from domains.parameters.models.voting_type import VotingType


@pytest.mark.django_db
class TestVotingTypeForm:

    def _valid_data(self):
        return {
            'description': 'Assembleia Geral Ordinária',
            'is_active': True,
        }

    def test_form_valid(self):
        form = VotingTypeForm(data=self._valid_data())
        assert form.is_valid()
        assert form.errors == {}

    def test_description_required(self):
        data = self._valid_data()
        del data['description']
        form = VotingTypeForm(data=data)
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_blank_spaces(self):
        data = self._valid_data()
        data['description'] = '   '
        form = VotingTypeForm(data=data)
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_stripped(self):
        data = self._valid_data()
        data['description'] = '   Votação de Título   '
        form = VotingTypeForm(data=data)
        assert form.is_valid()
        assert form.cleaned_data['description'] == 'Votação de Título'

    def test_description_duplicated(self):
        VotingType.objects.create(description='Votação Duplicada')
        data = self._valid_data()
        data['description'] = 'Votação Duplicada'
        form = VotingTypeForm(data=data)
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_edit_preserves_own_record(self):
        voting_type = VotingType.objects.create(description='Votação My Própria')
        form = VotingTypeForm(data={
            'description': 'Votação My Própria',
            'is_active': True,
        }, instance=voting_type)
        assert form.is_valid()

    def test_default_is_active_true_model(self):
        instance = VotingType(description='Votação Padrão')
        assert instance.is_active is True

    def test_is_active_true_preserved_by_form(self):
        form = VotingTypeForm(data={
            'description': 'Votação Padrão',
            'is_active': True,
        })
        assert form.is_valid()
        instance = form.save()
        assert instance.is_active is True

    def test_error_messages(self):
        form = VotingTypeForm(data={})
        assert not form.is_valid()
        assert 'A descrição é obrigatória.' in form.errors['description']

    def test_widget_placeholders(self):
        form = VotingTypeForm()
        widget = form.fields['description'].widget
        assert widget.attrs.get('placeholder') == 'Informe a descrição do tipo de votação'
        assert widget.attrs.get('maxlength') == '255'

    def test_is_active_widget(self):
        form = VotingTypeForm()
        widget = form.fields['is_active'].widget
        assert isinstance(widget, django_forms.CheckboxInput)

    def test_audit_fields_not_editable(self):
        form = VotingTypeForm()
        assert 'created_at' not in form.fields
        assert 'updated_at' not in form.fields