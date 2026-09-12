import pytest
from django.contrib.admin.sites import AdminSite
from domains.administrative.models import ChartOfAccount
from domains.administrative.admin import ChartOfAccountAdmin
from domains.administrative.forms import ChartOfAccountForm


@pytest.mark.django_db
class TestChartOfAccountAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = ChartOfAccountAdmin(ChartOfAccount, self.site)

    def test_admin_registered(self):
        assert self.admin is not None

    def test_admin_form(self):
        assert self.admin.form == ChartOfAccountForm

    def test_admin_list_display(self):
        expected = (
            'account_code', 'account_name', 'condominium',
            'account_type', 'account_class', 'account_level',
            'status', 'is_default',
            'effective_start_date', 'effective_end_date',
        )
        assert self.admin.list_display == expected

    def test_admin_list_filter(self):
        expected = (
            'condominium', 'account_type', 'account_class',
            'status', 'account_level', 'is_default',
            'is_system_account', 'can_be_archived',
        )
        assert self.admin.list_filter == expected

    def test_admin_search_fields(self):
        expected = (
            'account_code', 'account_name', 'external_reference',
            'condominium__name',
        )
        assert self.admin.search_fields == expected

    def test_admin_readonly_fields(self):
        expected = (
            'created_at', 'created_by', 'updated_at', 'updated_by',
            'approved_at', 'approved_by',
        )
        assert self.admin.readonly_fields == expected

    def test_admin_fieldsets_have_three_tabs(self):
        fieldsets = self.admin.fieldsets
        assert len(fieldsets) == 3
        tab_names = [title for title, _ in fieldsets]
        assert 'Principal' in tab_names
        assert 'Controle' in tab_names
        assert 'Auditoria' in tab_names
