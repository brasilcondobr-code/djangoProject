import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import User
from django.test import RequestFactory
from domains.parameters.admin import AssemblyStatusAdmin
from domains.parameters.forms import AssemblyStatusForm
from domains.parameters.models.assembly_status import AssemblyStatus


@pytest.mark.django_db
class TestAssemblyStatusAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = AssemblyStatusAdmin(AssemblyStatus, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, AssemblyStatusAdmin)
        assert global_admin.site.is_registered(AssemblyStatus)

    def test_admin_form(self):
        assert self.admin.form == AssemblyStatusForm

    def test_admin_list_display(self):
        expected = (
            'description', 'is_pending', 'is_running', 'is_complete',
            'is_active', 'created_at', 'updated_at',
        )
        assert self.admin.list_display == expected

    def test_admin_search_fields(self):
        assert self.admin.search_fields == ('description',)

    def test_admin_list_filter(self):
        assert self.admin.list_filter == (
            'is_pending', 'is_running', 'is_complete', 'is_active'
        )

    def test_admin_readonly_fields(self):
        assert self.admin.readonly_fields == ('created_at', 'updated_at')

    def test_admin_ordering(self):
        assert self.admin.ordering == ('description',)

    def test_admin_changelist_accessible(self):
        request = self.factory.get('/admin/parameters/assemblystatus/')
        request.user = User.objects.create_superuser('admin')
        changelist = ChangeList(
            request, AssemblyStatus, self.admin.list_display,
            self.admin.list_display_links, self.admin.list_filter,
            self.admin.date_hierarchy, self.admin.search_fields,
            self.admin.list_select_related, self.admin.list_per_page,
            self.admin.list_max_show_all, self.admin.list_editable, self.admin,
            self.admin.get_sortable_by(request), self.admin.search_help_text,
        )
        assert changelist is not None

    def test_admin_search_by_description(self):
        status = AssemblyStatus.objects.create(description='Assembleia Pendente')
        request = self.factory.get('/admin/parameters/assemblystatus/', {'q': 'pendente'})
        request.user = User.objects.create_superuser('admin')
        queryset = self.admin.get_search_results(
            request, AssemblyStatus.objects.all(), 'pendente'
        )[0]
        assert set(queryset) == {status}

    def test_admin_filter_by_status(self):
        running = AssemblyStatus.objects.create(
            description='Em execução', is_running=True, is_pending=False
        )
        AssemblyStatus.objects.create(description='Pendente')
        request = self.factory.get(
            '/admin/parameters/assemblystatus/', {'is_running__exact': '1'}
        )
        request.user = User.objects.create_superuser('admin')
        changelist = ChangeList(
            request, AssemblyStatus, self.admin.list_display,
            self.admin.list_display_links, self.admin.list_filter,
            self.admin.date_hierarchy, self.admin.search_fields,
            self.admin.list_select_related, self.admin.list_per_page,
            self.admin.list_max_show_all, self.admin.list_editable, self.admin,
            self.admin.get_sortable_by(request), self.admin.search_help_text,
        )
        assert set(changelist.get_queryset(request)) == {running}

    def test_form_reports_friendly_message_on_running_conflict(self):
        AssemblyStatus.objects.create(
            description='Em execução', is_running=True, is_pending=False
        )
        form = AssemblyStatusForm(
            data={'description': 'Outra execução', 'is_running': True}
        )
        assert not form.is_valid()
        assert 'execução' in str(form.non_field_errors()).lower()

    def test_form_reports_friendly_message_on_complete_conflict(self):
        AssemblyStatus.objects.create(
            description='Concluída', is_complete=True, is_pending=False
        )
        form = AssemblyStatusForm(
            data={'description': 'Outra concluída', 'is_complete': True}
        )
        assert not form.is_valid()
        assert 'completo' in str(form.non_field_errors()).lower()