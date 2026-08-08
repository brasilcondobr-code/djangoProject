import pytest
from django.db import IntegrityError
from domains.parameters.models.voting_type import VotingType


@pytest.mark.django_db
class TestVotingTypeModel:

    def test_create_valid(self):
        voting_type = VotingType.objects.create(description='Assembleia Ordinária')
        assert voting_type.pk is not None
        assert voting_type.description == 'Assembleia Ordinária'

    def test_description_required(self):
        with pytest.raises(IntegrityError):
            VotingType.objects.create(description=None)

    def test_description_max_length(self):
        field = VotingType._meta.get_field('description')
        assert field.max_length == 255

    def test_description_blank_false(self):
        field = VotingType._meta.get_field('description')
        assert field.blank is False
        assert field.null is False

    def test_description_unique(self):
        VotingType.objects.create(description='Assembleia Extraordinária')
        with pytest.raises(IntegrityError):
            VotingType.objects.create(description='Assembleia Extraordinária')

    def test_str_returns_description(self):
        voting_type = VotingType.objects.create(description='Votação de Orçamento')
        assert str(voting_type) == 'Votação de Orçamento'

    def test_default_is_active_true(self):
        voting_type = VotingType.objects.create(description='Votação de Condomínio')
        assert voting_type.is_active is True

    def test_created_at_auto_set(self):
        voting_type = VotingType.objects.create(description='Votação de Atas')
        assert voting_type.created_at is not None

    def test_updated_at_changes_on_update(self):
        voting_type = VotingType.objects.create(description='Votação Original')
        original_updated = voting_type.updated_at
        voting_type.description = 'Votação Atualizada'
        voting_type.save()
        voting_type.refresh_from_db()
        assert voting_type.updated_at >= original_updated

    def test_verbose_names(self):
        assert VotingType._meta.verbose_name == '22. Tipo de Votação'
        assert VotingType._meta.verbose_name_plural == '22. Tipos de Votações'