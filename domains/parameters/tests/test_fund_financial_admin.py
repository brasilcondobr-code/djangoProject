import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from domains.parameters.admin import FundFinancialAdmin
from domains.parameters.forms import FundFinancialForm
from domains.parameters.models import FundFinancial


@pytest.mark.django_db
class TestFundFinancialAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = FundFinancialAdmin(FundFinancial, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, FundFinancialAdmin)
        assert global_admin.site.is_registered(FundFinancial)

    def test_admin_form(self):
        assert self.admin.form == FundFinancialForm

    def test_admin_list_display(self):
        expected = (
            'description',
            'condominium',
            'is_active',
            'created_at',
            'updated_at',
        )
        assert self.admin.list_display == expected

    def test_admin_list_display_links(self):
        assert self.admin.list_display_links == ('description',)

    def test_admin_search_fields(self):
        assert self.admin.search_fields == (
            'description',
            'condominium__name',
            'condominium__code',
            'condominium__cnpj',
        )

    def test_admin_list_filter(self):
        assert self.admin.list_filter == (
            'condominium',
            'is_active',
        )

    def test_admin_ordering(self):
        assert self.admin.ordering == ('description',)

    def test_admin_readonly_fields(self):
        assert self.admin.readonly_fields == ('created_at', 'updated_at')

    def test_admin_autocomplete_fields(self):
        assert self.admin.autocomplete_fields == ('condominium',)

    def test_admin_list_select_related(self):
        assert self.admin.list_select_related == ('condominium',)

    def test_admin_list_per_page(self):
        assert self.admin.list_per_page == 25

    def test_admin_empty_value_display(self):
        assert self.admin.empty_value_display == '-'

    def test_admin_media_includes_custom_css(self):
        assert 'css/fund_financial_admin.css' in str(self.admin.media)

    def test_admin_fieldsets(self):
        assert self.admin.fieldsets[0][0] == 'Dados principais'
        assert self.admin.fieldsets[0][1]['fields'] == (
            'condominium',
            'description',
            'is_active',
        )
        assert self.admin.fieldsets[1][0] == 'Auditoria'
        assert self.admin.fieldsets[1][1]['classes'] == ('collapse',)
        assert self.admin.fieldsets[1][1]['fields'] == (
            'created_at',
            'updated_at',
        )


@pytest.mark.django_db
class TestFundFinancialAdminRender:

    @pytest.fixture(autouse=True)
    def setup(self, client, django_user_model):
        self.client = client
        self.user = django_user_model.objects.create_superuser(
            username='admin_fund',
            email='admin_fund@teste.com',
            password='admin123',
        )
        assert self.client.login(
            username='admin_fund',
            password='admin123',
        )

    def test_add_page_renders(self):
        response = self.client.get('/admin/parameters/fundfinancial/add/')

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Condomínio' in content
        assert 'Condomínio/Unidade' not in content
        assert 'Selecione o condomínio do fundo.' in content
        assert 'Informe a descrição do fundo' in content
        assert 'Dados principais' in content
        assert 'Auditoria' in content
        assert 'admin-autocomplete' in content
        assert 'css/fund_financial_admin.css' in content

    def test_changelist_renders(self, fund_condominium):
        FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )

        response = self.client.get('/admin/parameters/fundfinancial/')

        assert response.status_code == 200
        assert b'Fundo de Reserva' in response.content

    def test_create_via_post(self, fund_condominium):
        response = self.client.post(
            '/admin/parameters/fundfinancial/add/',
            {
                'condominium': str(fund_condominium.pk),
                'description': 'Fundo de Reserva',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )

        assert response.status_code == 302
        fund = FundFinancial.objects.get(description='Fundo de Reserva')
        assert fund.condominium == fund_condominium
        assert fund.is_active is True

    def test_create_duplicate_same_condominium_via_post_rejected(
        self, fund_condominium
    ):
        FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )

        response = self.client.post(
            '/admin/parameters/fundfinancial/add/',
            {
                'condominium': str(fund_condominium.pk),
                'description': 'FUNDO DE RESERVA',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )

        assert response.status_code == 200
        assert FundFinancial.objects.count() == 1
        assert (
            'Já existe um fundo com esta descrição para o '
            'condomínio selecionado.'
            in response.content.decode()
        )

    def test_create_same_description_different_condominium_via_post(
        self, fund_condominium, other_condominium
    ):
        FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )

        response = self.client.post(
            '/admin/parameters/fundfinancial/add/',
            {
                'condominium': str(other_condominium.pk),
                'description': 'Fundo de Reserva',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )

        assert response.status_code == 302
        assert FundFinancial.objects.count() == 2

    def test_change_page_renders_and_updates(self, fund_condominium):
        fund = FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo de Reserva',
        )
        change_url = (
            '/admin/parameters/fundfinancial/%s/change/' % fund.pk
        )

        response = self.client.get(change_url)
        assert response.status_code == 200

        response = self.client.post(
            change_url,
            {
                'condominium': str(fund_condominium.pk),
                'description': 'Fundo de Obras',
                'is_active': 'on',
                '_save': 'Salvar',
            },
        )

        assert response.status_code == 302
        fund.refresh_from_db()
        assert fund.description == 'Fundo de Obras'

    def test_delete_via_admin(self, fund_condominium):
        fund = FundFinancial.objects.create(
            condominium=fund_condominium,
            description='Fundo a Ser Removido',
        )
        delete_url = (
            '/admin/parameters/fundfinancial/%s/delete/' % fund.pk
        )

        response = self.client.get(delete_url)
        assert response.status_code == 200

        response = self.client.post(delete_url, {'post': 'Sim'})

        assert response.status_code == 302
        assert not FundFinancial.objects.filter(pk=fund.pk).exists()
