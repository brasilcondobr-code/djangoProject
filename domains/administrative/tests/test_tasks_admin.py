import pytest
from django.contrib.admin.sites import AdminSite
from domains.administrative.models.task import Task
from domains.administrative.admin import TaskAdmin
from domains.administrative.forms.tasks_form import TaskForm


@pytest.mark.django_db
class TestTaskAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = TaskAdmin(Task, self.site)

    def test_admin_registered(self):
        assert self.admin is not None

    def test_admin_form(self):
        assert self.admin.form == TaskForm

    def test_admin_list_display(self):
        expected = (
            'condominium', 'title', 'responsible_user', 'status',
            'release_date', 'estimated_completion_date',
            'is_active', 'created_at', 'updated_at',
        )
        assert self.admin.list_display == expected

    def test_admin_list_filter(self):
        expected = ('is_active', 'status', 'condominium')
        assert self.admin.list_filter == expected

    def test_admin_search_fields(self):
        expected = (
            'title', 'condominium__name',
            'responsible_user__username', 'responsible_user__email',
        )
        assert self.admin.search_fields == expected

    def test_admin_readonly_fields(self):
        expected = ('created_by_user', 'created_at', 'updated_at')
        assert self.admin.readonly_fields == expected

    def test_admin_fieldsets_has_principal(self):
        fieldsets = self.admin.fieldsets
        assert len(fieldsets) == 1
        assert fieldsets[0][0] == 'Principal'

    def test_admin_fields_in_principal(self):
        fieldsets = self.admin.fieldsets
        fields = fieldsets[0][1]['fields']
        assert 'condominium' in fields
        assert 'created_by_user' in fields
        assert 'responsible_user' in fields
        assert 'title' in fields
        assert 'release_date' in fields
        assert 'estimated_completion_date' in fields
        assert 'completion_date' in fields
        assert 'description' in fields
        assert 'is_active' in fields
        assert 'status' in fields
