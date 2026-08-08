import pytest
from domains.parameters.models.voting_type import VotingType
from domains.parameters.services.voting_type_service import VotingTypeService


@pytest.mark.django_db
class TestVotingTypeService:

    def test_create_voting_type(self):
        voting_type = VotingTypeService.create_voting_type(
            {'description': '  Assembleia Geral Ordinária  ', 'is_active': True}
        )
        assert voting_type.pk is not None
        assert voting_type.description == 'Assembleia Geral Ordinária'

    def test_update_voting_type(self):
        voting_type = VotingType.objects.create(description='Votação Original')
        updated = VotingTypeService.update_voting_type(
            voting_type, {'description': 'Votação Atualizada'}
        )
        updated.refresh_from_db()
        assert updated.description == 'Votação Atualizada'

    def test_normalize_description(self):
        normalized = VotingTypeService.normalize_description('  Assembleia   ')
        assert normalized == 'Assembleia'

    def test_normalize_description_none(self):
        assert VotingTypeService.normalize_description(None) is None

    def test_create_rejects_duplicate_case_insensitive(self):
        VotingTypeService.create_voting_type({'description': 'Assembleia'})
        with pytest.raises(ValueError):
            VotingTypeService.create_voting_type({'description': ' ASSEMBLEIA '})

    def test_update_rejects_duplicate_case_insensitive(self):
        voting_type = VotingType.objects.create(description='Consulta')
        other = VotingType.objects.create(description='Votação')
        with pytest.raises(ValueError):
            VotingTypeService.update_voting_type(other, {'description': 'consulta'})

    def test_delete_voting_type(self):
        voting_type = VotingType.objects.create(description='Votação Removida')
        VotingTypeService.delete_voting_type(voting_type)
        assert not VotingType.objects.filter(pk=voting_type.pk).exists()

    def test_toggle_active(self):
        voting_type = VotingType.objects.create(description='Votação Estado')
        VotingTypeService.toggle_active(voting_type, False)
        voting_type.refresh_from_db()
        assert voting_type.is_active is False