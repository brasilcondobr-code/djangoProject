import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from domains.parameters.admin import ConciergeServiceCategoryAdmin
from domains.parameters.forms import ConciergeServiceCategoryForm
from domains.parameters.models.concierge_service_categories import ConciergeServiceCategory


@pytest.mark.django_db
class TestConciergeServiceCategoryAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = ConciergeServiceCategoryAdmin(ConciergeServiceCategory, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, ConciergeServiceCategoryAdmin)
        assert global_admin.site.is_registered(ConciergeServiceCategory)

    def test_admin_form(self):
        assert self.admin.form == ConciergeServiceCategoryForm

    def test_admin_list_display(self):
        expected = ('description', 'is_active', 'created_at', 'updated_at')
        assert self.admin.list_display == expected

    def test_admin_list_display_links(self):
        assert self.admin.list_display_links == ('description',)

    def test_admin_search_fields(self):
        assert self.admin.search_fields == ('description',)

    def test_admin_list_filter(self):
        assert self.admin.list_filter == ('is_active',)

    def test_admin_ordering(self):
        assert self.admin.ordering == ('description',)

    def test_admin_readonly_fields(self):
        assert self.admin.readonly_fields == ('created_at', 'updated_at')

    def test_admin_list_per_page(self):
        assert self.admin.list_per_page == 25

    def test_admin_empty_value_display(self):
        assert self.admin.empty_value_display == '-'

    def test_admin_fieldsets(self):
        assert self.admin.fieldsets[0][0] == 'Dados principais'
        assert self.admin.fieldsets[0][1]['fields'] == ('description', 'is_active')
        assert self.admin.fieldsets[1][0] == 'Auditoria'
        assert self.admin.fieldsets[1][1]['classes'] == ('collapse',)
        assert self.admin.fieldsets[1][1]['fields'] == ('created_at', 'updated_at')

    def test_admin_save_new_sets_audit_fields(self):
        category = ConciergeServiceCategory(description='Faxineira')
        self.admin.save_model(None, category, form=None, change=False)
        assert category.pk is not None
        assert category.created_at is not None
        assert category.updated_at is not None


@pytest.mark.django_db
class TestConciergeServiceCategoryAdminRender:

    @pytest.fixture(autouse=True)
    def setup(self, client, django_user_model):
        self.client = client
        self.user = django_user_model.objects.create_superuser(
            username='admin_csc', email='admin_csc@teste.com', password='admin123'
        )
        assert self.client.login(username='admin_csc', password='admin123')

    def test_add_page_renders(self):
        response = self.client.get('/admin/parameters/conciergeservicecategory/add/')
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Informe a descrição da categoria de serviço portaria' in content
        assert 'form-control' in content

    def test_changelist_renders(self):
        ConciergeServiceCategory.objects.create(description='Segurança Patrimonial')
        response = self.client.get('/admin/parameters/conciergeservicecategory/')
        assert response.status_code == 200
        assert b'Seguran' in response.content

    def test_create_via_post(self):
        response = self.client.post(
            '/admin/parameters/conciergeservicecategory/add/',
            {
                'description': 'Portaria 24 horas',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 302
        category = ConciergeServiceCategory.objects.get(description='Portaria 24 horas')
        assert category.is_active is True

    def test_create_duplicate_via_post_rejected(self):
        ConciergeServiceCategory.objects.create(description='Encomendas')
        response = self.client.post(
            '/admin/parameters/conciergeservicecategory/add/',
            {
                'description': 'ENCOMENDAS',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 200
        assert ConciergeServiceCategory.objects.filter(description='Encomendas').count() == 1
        assert not ConciergeServiceCategory.objects.filter(description='ENCOMENDAS').exists()
        assert 'Já existe uma categoria de serviço portaria' in response.content.decode()

    def test_change_page_renders_and_updates(self):
        category = ConciergeServiceCategory.objects.create(description='Elevador')
        change_url = '/admin/parameters/conciergeservicecategory/%s/change/' % category.pk
        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            {
                'description': 'Elevador e Escada Rolante',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 302
        category.refresh_from_db()
        assert category.description == 'Elevador e Escada Rolante'

    def test_delete_via_admin(self):
        category = ConciergeServiceCategory.objects.create(description='A Ser Removida')
        delete_url = '/admin/parameters/conciergeservicecategory/%s/delete/' % category.pk
        response = self.client.get(delete_url)
        assert response.status_code == 200

        response = self.client.post(delete_url, {'post': 'Sim'})
        assert response.status_code == 302
        assert not ConciergeServiceCategory.objects.filter(pk=category.pk).exists()
