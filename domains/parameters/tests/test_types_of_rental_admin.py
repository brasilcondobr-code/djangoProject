import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from domains.parameters.admin import TypesOfRentalAdmin
from domains.parameters.forms import TypesOfRentalForm
from domains.parameters.models.types_of_rental import TypesOfRental


@pytest.mark.django_db
class TestTypesOfRentalAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = TypesOfRentalAdmin(TypesOfRental, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, TypesOfRentalAdmin)
        assert global_admin.site.is_registered(TypesOfRental)

    def test_admin_form(self):
        assert self.admin.form == TypesOfRentalForm

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
        assert self.admin.fieldsets[1][0] == 'Limites'
        assert self.admin.fieldsets[1][1]['fields'] == ('numberOfAppointments', 'numberOfReservations')
        assert self.admin.fieldsets[2][0] == 'Auditoria'
        assert self.admin.fieldsets[2][1]['classes'] == ('collapse',)
        assert self.admin.fieldsets[2][1]['fields'] == ('created_at', 'updated_at')

    def test_admin_save_new_sets_audit_fields(self):
        rental = TypesOfRental(description='Locação Residencial')
        self.admin.save_model(None, rental, form=None, change=False)
        assert rental.pk is not None
        assert rental.created_at is not None
        assert rental.updated_at is not None


@pytest.mark.django_db
class TestTypesOfRentalAdminRender:

    @pytest.fixture(autouse=True)
    def setup(self, client, django_user_model):
        self.client = client
        self.user = django_user_model.objects.create_superuser(
            username='admin_tor', email='admin_tor@teste.com', password='admin123'
        )
        assert self.client.login(username='admin_tor', password='admin123')

    def test_add_page_renders(self):
        response = self.client.get('/admin/parameters/typesofrental/add/')
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Informe a descrição do tipo de locação' in content
        assert 'form-control' in content
        assert 'numberOfAppointments' in content
        assert 'numberOfReservations' in content

    def test_changelist_renders(self):
        TypesOfRental.objects.create(description='Locação Comercial')
        response = self.client.get('/admin/parameters/typesofrental/')
        assert response.status_code == 200
        assert b'Loca' in response.content

    def test_create_via_post(self):
        response = self.client.post(
            '/admin/parameters/typesofrental/add/',
            {
                'description': 'Locação Residencial',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 302
        rental = TypesOfRental.objects.get(description='Locação Residencial')
        assert rental.is_active is True

    def test_create_duplicate_via_post_rejected(self):
        TypesOfRental.objects.create(description='Locacao Comercial')
        response = self.client.post(
            '/admin/parameters/typesofrental/add/',
            {
                'description': 'LOCACAO COMERCIAL',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 200
        assert TypesOfRental.objects.filter(description='Locacao Comercial').count() == 1
        assert not TypesOfRental.objects.filter(description='LOCACAO COMERCIAL').exists()
        assert 'Já existe um tipo de locação' in response.content.decode()

    def test_change_page_renders_and_updates(self):
        rental = TypesOfRental.objects.create(description='Locação Anual')
        change_url = '/admin/parameters/typesofrental/%s/change/' % rental.pk
        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            {
                'description': 'Locação Anual Renovada',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 302
        rental.refresh_from_db()
        assert rental.description == 'Locação Anual Renovada'

    def test_delete_via_admin(self):
        rental = TypesOfRental.objects.create(description='A Ser Removida')
        delete_url = '/admin/parameters/typesofrental/%s/delete/' % rental.pk
        response = self.client.get(delete_url)
        assert response.status_code == 200

        response = self.client.post(delete_url, {'post': 'Sim'})
        assert response.status_code == 302
        assert not TypesOfRental.objects.filter(pk=rental.pk).exists()
