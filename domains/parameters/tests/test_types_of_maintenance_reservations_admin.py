import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from domains.parameters.admin import TypesOfMaintenanceReservationsAdmin
from domains.parameters.forms import TypesOfMaintenanceReservationsForm
from domains.parameters.models.types_of_maintenance_reservations import (
    TypesOfMaintenanceReservations,
)


@pytest.mark.django_db
class TestTypesOfMaintenanceReservationsAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = TypesOfMaintenanceReservationsAdmin(
            TypesOfMaintenanceReservations, self.site
        )
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, TypesOfMaintenanceReservationsAdmin)
        assert global_admin.site.is_registered(TypesOfMaintenanceReservations)

    def test_admin_form(self):
        assert self.admin.form == TypesOfMaintenanceReservationsForm

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
        maintenance = TypesOfMaintenanceReservations(
            description='Manutenção Preventiva'
        )
        self.admin.save_model(None, maintenance, form=None, change=False)
        assert maintenance.pk is not None
        assert maintenance.created_at is not None
        assert maintenance.updated_at is not None


@pytest.mark.django_db
class TestTypesOfMaintenanceReservationsAdminRender:

    @pytest.fixture(autouse=True)
    def setup(self, client, django_user_model):
        self.client = client
        self.user = django_user_model.objects.create_superuser(
            username='admin_tmr', email='admin_tmr@teste.com', password='admin123'
        )
        assert self.client.login(username='admin_tmr', password='admin123')

    def test_add_page_renders(self):
        response = self.client.get('/admin/parameters/typesofmaintenancereservations/add/')
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Informe a descrição do tipo de manutenção' in content
        assert 'form-control' in content
        assert 'is_active' in content

    def test_changelist_renders(self):
        TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Corretiva'
        )
        response = self.client.get('/admin/parameters/typesofmaintenancereservations/')
        assert response.status_code == 200
        assert b'Manuten' in response.content

    def test_create_via_post(self):
        response = self.client.post(
            '/admin/parameters/typesofmaintenancereservations/add/',
            {
                'description': 'Manutenção Preventiva',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 302
        maintenance = TypesOfMaintenanceReservations.objects.get(
            description='Manutenção Preventiva'
        )
        assert maintenance.is_active is True

    def test_create_duplicate_via_post_rejected(self):
        TypesOfMaintenanceReservations.objects.create(
            description='Manutencao Corretiva'
        )
        response = self.client.post(
            '/admin/parameters/typesofmaintenancereservations/add/',
            {
                'description': 'MANUTENCAO CORRETIVA',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 200
        assert (
            TypesOfMaintenanceReservations.objects.filter(
                description='Manutencao Corretiva'
            ).count()
            == 1
        )
        assert not TypesOfMaintenanceReservations.objects.filter(
            description='MANUTENCAO CORRETIVA'
        ).exists()
        assert 'Já existe um tipo de manutenção' in response.content.decode()

    def test_change_page_renders_and_updates(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Hidráulica'
        )
        change_url = (
            '/admin/parameters/typesofmaintenancereservations/%s/change/'
            % maintenance.pk
        )
        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            {
                'description': 'Manutenção Hidráulica Preventiva',
                '_save': 'Salvar',
            },
        )
        assert response.status_code == 302
        maintenance.refresh_from_db()
        assert maintenance.description == 'Manutenção Hidráulica Preventiva'

    def test_delete_via_admin(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='A Ser Removida'
        )
        delete_url = (
            '/admin/parameters/typesofmaintenancereservations/%s/delete/'
            % maintenance.pk
        )
        response = self.client.get(delete_url)
        assert response.status_code == 200

        response = self.client.post(delete_url, {'post': 'Sim'})
        assert response.status_code == 302
        assert not TypesOfMaintenanceReservations.objects.filter(
            pk=maintenance.pk
        ).exists()
