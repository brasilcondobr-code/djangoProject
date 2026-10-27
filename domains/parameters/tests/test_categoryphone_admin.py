import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from domains.parameters.admin import CategoryPhoneAdmin
from domains.parameters.forms import CategoryPhoneForm
from domains.parameters.models.categoryphone import CategoryPhone


@pytest.mark.django_db
class TestCategoryPhoneAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = CategoryPhoneAdmin(CategoryPhone, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, CategoryPhoneAdmin)
        assert global_admin.site.is_registered(CategoryPhone)

    def test_admin_form(self):
        assert self.admin.form == CategoryPhoneForm

    def test_admin_list_display(self):
        assert self.admin.list_display == ('name', 'is_active')

    def test_admin_list_display_links(self):
        assert self.admin.list_display_links == ('name',)

    def test_admin_search_fields(self):
        assert self.admin.search_fields == ('name',)

    def test_admin_list_filter(self):
        assert self.admin.list_filter == ('is_active',)

    def test_admin_ordering(self):
        assert self.admin.ordering == ('name',)

    def test_admin_list_per_page(self):
        assert self.admin.list_per_page == 25

    def test_admin_empty_value_display(self):
        assert self.admin.empty_value_display == '-'

    def test_admin_fieldsets(self):
        assert self.admin.fieldsets[0][0] == 'Dados principais'
        assert self.admin.fieldsets[0][1]['fields'] == ('name', 'is_active')


@pytest.mark.django_db
class TestCategoryPhoneAdminRender:

    @pytest.fixture(autouse=True)
    def setup(self, client, django_user_model):
        self.client = client
        self.user = django_user_model.objects.create_superuser(
            username='admin_cp', email='admin_cp@teste.com', password='admin123'
        )
        assert self.client.login(username='admin_cp', password='admin123')

    def test_add_page_renders(self):
        response = self.client.get('/admin/parameters/categoryphone/add/')
        assert response.status_code == 200
        content = response.content.decode()
        assert 'id="id_name"' in content
        assert 'Informe o nome da categoria de telefone' in content
        assert 'form-control' in content

    def test_changelist_renders(self):
        CategoryPhone.objects.create(name='Academia')
        response = self.client.get('/admin/parameters/categoryphone/')
        assert response.status_code == 200
        assert b'Academia' in response.content

    def test_create_via_post(self):
        response = self.client.post(
            '/admin/parameters/categoryphone/add/',
            {'name': 'Zeladoria', 'is_active': 'on'},
        )
        assert response.status_code == 302
        assert CategoryPhone.objects.filter(name='Zeladoria', is_active=True).exists()

    def test_create_duplicate_via_post_rejected(self):
        CategoryPhone.objects.create(name='Academia')
        response = self.client.post(
            '/admin/parameters/categoryphone/add/',
            {'name': 'ACADEMIA', 'is_active': 'on'},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Já existe uma categoria de telefone' in content
        assert CategoryPhone.objects.count() == 1

    def test_change_via_post(self):
        category = CategoryPhone.objects.create(name='Academia')
        response = self.client.post(
            '/admin/parameters/categoryphone/%s/change/' % category.pk,
            {'name': 'Academia Nova', 'is_active': 'on'},
        )
        assert response.status_code == 302
        category.refresh_from_db()
        assert category.name == 'Academia Nova'
