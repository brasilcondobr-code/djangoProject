import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory

from domains.parameters.admin import FinancialTransactionAdmin
from domains.parameters.forms import FinancialTransactionForm
from domains.parameters.models.financial_transaction import FinancialTransaction


@pytest.mark.django_db
class TestFinancialTransactionAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = FinancialTransactionAdmin(FinancialTransaction, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, FinancialTransactionAdmin)
        assert global_admin.site.is_registered(FinancialTransaction)

    def test_admin_form(self):
        assert self.admin.form == FinancialTransactionForm

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

    def test_admin_fieldsets(self):
        fieldsets = dict(self.admin.fieldsets)

        assert fieldsets['Dados principais']['fields'] == (
            'description', 'is_active',
        )
        assert fieldsets['Auditoria']['fields'] == ('created_at', 'updated_at')

    def test_admin_search_returns_matching(self):
        transaction = FinancialTransaction.objects.create(description='Água')
        FinancialTransaction.objects.create(description='Energia')
        request = self.factory.get(
            '/admin/parameters/financialtransaction/', {'q': 'gua'}
        )
        request.user = User.objects.create_superuser('admin')
        queryset = self.admin.get_search_results(
            request, FinancialTransaction.objects.all(), 'gua'
        )[0]

        assert set(queryset) == {transaction}

    def test_admin_filter_by_active(self):
        active = FinancialTransaction.objects.create(description='Ativa')
        FinancialTransaction.objects.create(
            description='Inativa', is_active=False
        )
        request = self.factory.get(
            '/admin/parameters/financialtransaction/',
            {'is_active__exact': '1'},
        )
        request.user = User.objects.create_superuser('admin')
        queryset = self.admin.get_queryset(request).filter(is_active=True)

        assert set(queryset) == {active}

    def test_admin_has_change_form_permission(self):
        request = self.factory.get('/admin/parameters/financialtransaction/')
        request.user = User.objects.create_superuser('admin')

        assert self.admin.has_change_permission(request) is True

    def test_admin_has_add_permission(self):
        request = self.factory.get('/admin/parameters/financialtransaction/add/')
        request.user = User.objects.create_superuser('admin')

        assert self.admin.has_add_permission(request) is True

    def test_admin_has_delete_permission(self):
        request = self.factory.get(
            '/admin/parameters/financialtransaction/1/delete/'
        )
        request.user = User.objects.create_superuser('admin')

        assert self.admin.has_delete_permission(request) is True
