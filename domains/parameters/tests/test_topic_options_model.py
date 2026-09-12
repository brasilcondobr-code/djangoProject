import pytest
from django.db import IntegrityError
from domains.parameters.models.topic_options import TopicOption



@pytest.mark.django_db
class TestTopicOptionModel:

    def test_create_valid(self):
        topic_option = TopicOption.objects.create(description='Orçamento anual')
        assert topic_option.pk is not None
        assert topic_option.description == 'Orçamento anual'

    def test_default_is_active_true(self):
        topic_option = TopicOption.objects.create(description='Prestação de contas')
        assert topic_option.is_active is True

    def test_created_at_auto_set(self):
        topic_option = TopicOption.objects.create(description='Deliberações')
        assert topic_option.created_at is not None

    def test_updated_at_changes_on_update(self):
        topic_option = TopicOption.objects.create(description='Pauta Original')
        original_updated = topic_option.updated_at
        topic_option.description = 'Pauta Atualizada'
        topic_option.save()
        topic_option.refresh_from_db()
        assert topic_option.updated_at >= original_updated

    def test_str_returns_description(self):
        topic_option = TopicOption.objects.create(description='Eleições')
        assert str(topic_option) == 'Eleições'

    def test_duplicate_description_raises(self):
        TopicOption.objects.create(description='Assembleia Geral')
        with pytest.raises(IntegrityError):
            TopicOption.objects.create(description='Assembleia Geral')

    def test_description_required(self):
        with pytest.raises(IntegrityError):
            TopicOption.objects.create(description=None)

    def test_description_max_length(self):
        field = TopicOption._meta.get_field('description')
        assert field.max_length == 255

    def test_verbose_names(self):
        assert TopicOption._meta.verbose_name == '24. Opção de Pauta'
        assert TopicOption._meta.verbose_name_plural == '24. Opções de Pautas'