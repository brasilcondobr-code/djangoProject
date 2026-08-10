import pytest
from domains.parameters.forms import TopicOptionForm
from domains.parameters.models.topic_options import TopicOption


@pytest.mark.django_db
class TestTopicOptionForm:

    def test_form_valid(self):
        form = TopicOptionForm(data={'description': 'Orçamento anual'})
        assert form.is_valid(), form.errors

    def test_description_required(self):
        form = TopicOptionForm(data={'description': ''})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_description_only_spaces(self):
        form = TopicOptionForm(data={'description': '   '})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_duplicate_description(self):
        TopicOption.objects.create(description='Eleições')
        form = TopicOptionForm(data={'description': 'Eleições'})
        assert not form.is_valid()
        assert 'description' in form.errors
        assert 'Já existe uma opção de pauta' in str(form.errors['description'])

    def test_duplicate_description_case_insensitive(self):
        TopicOption.objects.create(description='Prestação de Contas')
        form = TopicOptionForm(data={'description': 'prestação de contas'})
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_whitespace_normalized(self):
        form = TopicOptionForm(data={'description': '  Deliberações  '})
        assert form.is_valid(), form.errors
        assert form.cleaned_data['description'] == 'Deliberações'

    def test_own_description_on_edit(self):
        topic_option = TopicOption.objects.create(description='Votação')
        form = TopicOptionForm(
            instance=topic_option,
            data={'description': 'Votação  '},
        )
        assert form.is_valid(), form.errors

    def test_is_active_default(self):
        form = TopicOptionForm()
        assert form.fields['is_active'].initial is True

    def test_error_messages(self):
        form = TopicOptionForm(data={'description': ''})
        assert not form.is_valid()
        assert 'Informe a descrição' in str(form.errors['description'])

    def test_widgets(self):
        form = TopicOptionForm()
        assert form.fields['description'].widget.attrs.get('placeholder') is not None
        assert form.fields['description'].widget.attrs.get('maxlength') == '255'