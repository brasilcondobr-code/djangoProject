import pytest

from domains.parameters.models.types_of_rental import TypesOfRental
from domains.parameters.services.types_of_rental_service import (
    TypesOfRentalService,
)


@pytest.mark.django_db
class TestTypesOfRentalService:

    def test_create_types_of_rental(self):
        rental = TypesOfRentalService.create_types_of_rental(
            {'description': '  Locação Residencial  ', 'is_active': True}
        )
        assert rental.pk is not None
        assert rental.description == 'Locação Residencial'
        assert rental.is_active is True

    def test_create_duplicate_rejected(self):
        TypesOfRentalService.create_types_of_rental(
            {'description': 'Locação Comercial'}
        )
        with pytest.raises(ValueError) as exc:
            TypesOfRentalService.create_types_of_rental(
                {'description': 'Locação Comercial'}
            )
        assert 'Já existe um tipo de locação' in str(exc.value)
        assert TypesOfRental.objects.count() == 1

    def test_create_duplicate_case_insensitive_rejected(self):
        TypesOfRentalService.create_types_of_rental(
            {'description': 'Locacao Anual'}
        )
        with pytest.raises(ValueError):
            TypesOfRentalService.create_types_of_rental(
                {'description': ' locacao anual '}
            )
        assert TypesOfRental.objects.count() == 1

    @pytest.mark.parametrize('invalid_description', ['', None, '   '])
    def test_create_invalid_description_rejected(self, invalid_description):
        with pytest.raises(ValueError) as exc:
            TypesOfRentalService.create_types_of_rental(
                {'description': invalid_description}
            )
        assert 'A descrição é obrigatória.' in str(exc.value)
        assert TypesOfRental.objects.count() == 0

    def test_update_types_of_rental(self):
        rental = TypesOfRental.objects.create(description='Original')
        updated = TypesOfRentalService.update_types_of_rental(
            rental, {'description': '  Atualizada  '}
        )
        updated.refresh_from_db()
        assert updated.description == 'Atualizada'

    def test_update_own_description_allowed(self):
        rental = TypesOfRental.objects.create(description='Guarita')
        updated = TypesOfRentalService.update_types_of_rental(
            rental, {'description': 'Guarita'}
        )
        assert updated.pk == rental.pk

    def test_update_duplicate_rejected(self):
        TypesOfRental.objects.create(description='Mala Direta')
        other = TypesOfRental.objects.create(description='Aviso Prévio')
        with pytest.raises(ValueError) as exc:
            TypesOfRentalService.update_types_of_rental(
                other, {'description': 'mala direta'}
            )
        assert 'Já existe um tipo de locação' in str(exc.value)
        other.refresh_from_db()
        assert other.description == 'Aviso Prévio'

    def test_update_empty_description_rejected(self):
        rental = TypesOfRental.objects.create(description='Não Vazio')
        with pytest.raises(ValueError) as exc:
            TypesOfRentalService.update_types_of_rental(
                rental, {'description': '   '}
            )
        assert 'A descrição é obrigatória.' in str(exc.value)
        rental.refresh_from_db()
        assert rental.description == 'Não Vazio'

    def test_update_is_active_without_description(self):
        rental = TypesOfRental.objects.create(description='Suspensa')
        updated = TypesOfRentalService.update_types_of_rental(
            rental, {'is_active': False}
        )
        updated.refresh_from_db()
        assert updated.is_active is False
        assert updated.description == 'Suspensa'

    def test_delete_types_of_rental(self):
        rental = TypesOfRental.objects.create(description='Removida')
        TypesOfRentalService.delete_types_of_rental(rental)
        assert not TypesOfRental.objects.filter(pk=rental.pk).exists()

    def test_toggle_active(self):
        rental = TypesOfRental.objects.create(description='Alternada')
        deactivated = TypesOfRentalService.toggle_active(rental, False)
        assert deactivated.is_active is False

        activated = TypesOfRentalService.toggle_active(deactivated, True)
        assert activated.is_active is True

    def test_normalize_description(self):
        assert TypesOfRentalService.normalize_description('  Chaveiro  ') == 'Chaveiro'

    def test_normalize_description_none(self):
        assert TypesOfRentalService.normalize_description(None) is None

    def test_normalize_description_internal_spaces_kept(self):
        assert (
            TypesOfRentalService.normalize_description('Recebe  e  entrega')
            == 'Recebe  e  entrega'
        )
