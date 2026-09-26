import pytest
from django.db import IntegrityError

from domains.parameters.models.concierge_service_categories import ConciergeServiceCategory


@pytest.mark.django_db
class TestConciergeServiceCategoryModel:

    def test_create_valid(self):
        category = ConciergeServiceCategory.objects.create(description='Entrega de encomendas')
        assert category.pk is not None
        assert category.description == 'Entrega de encomendas'

    def test_default_is_active_true(self):
        category = ConciergeServiceCategory.objects.create(description='Chaveiro')
        assert category.is_active is True

    def test_created_at_auto_set(self):
        category = ConciergeServiceCategory.objects.create(description='Portaria 24h')
        assert category.created_at is not None

    def test_updated_at_changes_on_update(self):
        category = ConciergeServiceCategory.objects.create(description='Recebimento')
        original_updated = category.updated_at
        category.description = 'Recebimento de pacotes'
        category.save()
        category.refresh_from_db()
        assert category.updated_at >= original_updated

    def test_str_returns_description(self):
        category = ConciergeServiceCategory.objects.create(description='Taxa de serviço')
        assert str(category) == 'Taxa de serviço'

    def test_duplicate_description_raises(self):
        ConciergeServiceCategory.objects.create(description='Limpeza')
        with pytest.raises(IntegrityError):
            ConciergeServiceCategory.objects.create(description='Limpeza')

    def test_description_required(self):
        with pytest.raises(IntegrityError):
            ConciergeServiceCategory.objects.create(description=None)

    def test_description_max_length(self):
        field = ConciergeServiceCategory._meta.get_field('description')
        assert field.max_length == 255

    def test_description_unique_flag(self):
        field = ConciergeServiceCategory._meta.get_field('description')
        assert field.unique is True

    def test_verbose_names(self):
        assert ConciergeServiceCategory._meta.verbose_name == '25. Categoria de Serviço Portaria'
        assert ConciergeServiceCategory._meta.verbose_name_plural == '25. Categorias de Serviço Portaria'

    def test_db_table(self):
        assert ConciergeServiceCategory._meta.db_table == 'parameters_conciergeservicecategories'

    def test_ordering(self):
        assert ConciergeServiceCategory._meta.ordering == ['description']

    def test_created_after_updated(self):
        first = ConciergeServiceCategory.objects.create(description='Aaa')
        second = ConciergeServiceCategory.objects.create(description='Bbb')
        assert list(ConciergeServiceCategory.objects.all()) == [first, second]
