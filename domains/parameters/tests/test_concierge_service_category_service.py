import pytest

from domains.parameters.models.concierge_service_categories import ConciergeServiceCategory
from domains.parameters.services.concierge_service_category_service import (
    ConciergeServiceCategoryService,
)


@pytest.mark.django_db
class TestConciergeServiceCategoryService:

    def test_create_concierge_service_category(self):
        category = ConciergeServiceCategoryService.create_concierge_service_category(
            {'description': '  Entrega de encomendas  ', 'is_active': True}
        )
        assert category.pk is not None
        assert category.description == 'Entrega de encomendas'
        assert category.is_active is True

    def test_create_duplicate_rejected(self):
        ConciergeServiceCategoryService.create_concierge_service_category(
            {'description': 'Segurança'}
        )
        with pytest.raises(ValueError) as exc:
            ConciergeServiceCategoryService.create_concierge_service_category(
                {'description': 'Segurança'}
            )
        assert 'Já existe uma categoria de serviço portaria' in str(exc.value)
        assert ConciergeServiceCategory.objects.count() == 1

    def test_create_duplicate_case_insensitive_rejected(self):
        ConciergeServiceCategoryService.create_concierge_service_category(
            {'description': 'Portaria'}
        )
        with pytest.raises(ValueError):
            ConciergeServiceCategoryService.create_concierge_service_category(
                {'description': ' PORTARIA '}
            )
        assert ConciergeServiceCategory.objects.count() == 1

    @pytest.mark.parametrize('invalid_description', ['', None, '   '])
    def test_create_invalid_description_rejected(self, invalid_description):
        with pytest.raises(ValueError) as exc:
            ConciergeServiceCategoryService.create_concierge_service_category(
                {'description': invalid_description}
            )
        assert 'A descrição é obrigatória.' in str(exc.value)
        assert ConciergeServiceCategory.objects.count() == 0

    def test_update_concierge_service_category(self):
        category = ConciergeServiceCategory.objects.create(description='Original')
        updated = ConciergeServiceCategoryService.update_concierge_service_category(
            category, {'description': '  Atualizada  '}
        )
        updated.refresh_from_db()
        assert updated.description == 'Atualizada'

    def test_update_own_description_allowed(self):
        category = ConciergeServiceCategory.objects.create(description='Guarita')
        updated = ConciergeServiceCategoryService.update_concierge_service_category(
            category, {'description': 'Guarita'}
        )
        assert updated.pk == category.pk

    def test_update_duplicate_rejected(self):
        ConciergeServiceCategory.objects.create(description='Mala Direta')
        other = ConciergeServiceCategory.objects.create(description='Aviso Prévio')
        with pytest.raises(ValueError) as exc:
            ConciergeServiceCategoryService.update_concierge_service_category(
                other, {'description': 'mala direta'}
            )
        assert 'Já existe uma categoria de serviço portaria' in str(exc.value)
        other.refresh_from_db()
        assert other.description == 'Aviso Prévio'

    def test_update_empty_description_rejected(self):
        category = ConciergeServiceCategory.objects.create(description='Não Vazio')
        with pytest.raises(ValueError) as exc:
            ConciergeServiceCategoryService.update_concierge_service_category(
                category, {'description': '   '}
            )
        assert 'A descrição é obrigatória.' in str(exc.value)
        category.refresh_from_db()
        assert category.description == 'Não Vazio'

    def test_update_is_active_without_description(self):
        category = ConciergeServiceCategory.objects.create(description='Suspensa')
        updated = ConciergeServiceCategoryService.update_concierge_service_category(
            category, {'is_active': False}
        )
        updated.refresh_from_db()
        assert updated.is_active is False
        assert updated.description == 'Suspensa'

    def test_delete_concierge_service_category(self):
        category = ConciergeServiceCategory.objects.create(description='Removida')
        ConciergeServiceCategoryService.delete_concierge_service_category(category)
        assert not ConciergeServiceCategory.objects.filter(pk=category.pk).exists()

    def test_toggle_active(self):
        category = ConciergeServiceCategory.objects.create(description='Alternada')
        deactivated = ConciergeServiceCategoryService.toggle_active(category, False)
        assert deactivated.is_active is False

        activated = ConciergeServiceCategoryService.toggle_active(deactivated, True)
        assert activated.is_active is True

    def test_normalize_description(self):
        assert ConciergeServiceCategoryService.normalize_description('  Chaveiro  ') == 'Chaveiro'

    def test_normalize_description_none(self):
        assert ConciergeServiceCategoryService.normalize_description(None) is None

    def test_normalize_description_internal_spaces_kept(self):
        assert (
            ConciergeServiceCategoryService.normalize_description('Recebe  e  entrega')
            == 'Recebe  e  entrega'
        )
