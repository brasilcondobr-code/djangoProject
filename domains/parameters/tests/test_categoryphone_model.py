import pytest

from domains.parameters.models.categoryphone import CategoryPhone


@pytest.mark.django_db
class TestCategoryPhoneModel:

    def test_create_valid(self):
        category = CategoryPhone.objects.create(name='Academia')
        assert category.pk is not None
        assert category.name == 'Academia'

    def test_default_is_active_true(self):
        category = CategoryPhone.objects.create(name='Portaria')
        assert category.is_active is True

    def test_str(self):
        assert str(CategoryPhone(name='Emergencia')) == 'Emergencia'

    def test_str_without_name(self):
        assert str(CategoryPhone()) == '26. Categoria de Telefone'

    def test_meta_verbose_numbered(self):
        assert CategoryPhone._meta.app_label == 'parameters'
        assert str(CategoryPhone._meta.verbose_name) == '26. Categoria de Telefone'
        assert str(CategoryPhone._meta.verbose_name_plural) == '26. Categorias de Telefone'

    def test_ordering(self):
        assert CategoryPhone._meta.ordering == ['name']

    def test_name_max_length_255(self):
        field = CategoryPhone._meta.get_field('name')
        assert field.max_length == 255
        assert field.blank is False
        assert field.null is False
