import pytest
from pytest_django.asserts import assertQuerysetEqual
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory
from domains.parameters.admin import VotingTypeAdmin
from domains.parameters.forms import VotingTypeForm
from domains.parameters.models.voting_type import VotingType


@pytest.mark.django_db
class TestVotingTypeAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = VotingTypeAdmin(VotingType, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        from django.contrib import admin as global_admin
        assert isinstance(self.admin, VotingTypeAdmin)
        assert global_admin.site.is_registered(VotingType)

    def test_admin_form(self):
        assert self.admin.form == VotingTypeForm

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

    def test_admin_fieldsets_has_principal(self):
        assert 'Dados principais' in dict(self.admin.fieldsets)
        assert 'Auditoria' in dict(self.admin.fieldsets)

    def test_admin_fields_in_principal(self):
        fields = dict(self.admin.fieldsets)['Dados principais']['fields']
        assert 'description' in fields
        assert 'is_active' in fields

    def test_admin_search_returns_matching(self):
        voting_type = VotingType.objects.create(description='Assembleia Ordinária')
        VotingType.objects.create(description='Consulta Popular')
        request = self.factory.get('/admin/parameters/votingtype/', {'q': 'assembleia'})
        request.user = User.objects.create_superuser('admin')
        queryset = self.admin.get_search_results(request, VotingType.objects.all(), 'assemble')[0]
        assert set(queryset) == {voting_type}

    def test_admin_get_queryset_returns_all(self):
        first = VotingType.objects.create(description='Votação Ativa')
        VotingType.objects.create(description='Votação Inativa', is_active=False)
        request = self.factory.get('/admin/parameters/votingtype/')
        request.user = User.objects.create_superuser('admin')
        queryset = self.admin.get_queryset(request)
        assert set(queryset) == {first, VotingType.objects.get(description='Votação Inativa')}

    def test_admin_changelist_filters_by_status(self):
        from django.contrib.admin.views.main import ChangeList
        active = VotingType.objects.create(description='Votação Ativa')
        VotingType.objects.create(description='Votação Inativa', is_active=False)
        request = self.factory.get('/admin/parameters/votingtype/', {'is_active__exact': '1'})
        request.user = User.objects.create_superuser('admin')
        changelist = ChangeList(
            request, VotingType, self.admin.list_display,
            self.admin.list_display_links, self.admin.list_filter,
            self.admin.date_hierarchy, self.admin.search_fields,
            self.admin.list_select_related, self.admin.list_per_page,
            self.admin.list_max_show_all, self.admin.list_editable, self.admin,
            self.admin.get_sortable_by(request), self.admin.search_help_text,
        )
        assert set(changelist.get_queryset(request)) == {active}