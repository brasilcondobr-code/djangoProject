import pytest
from django.contrib import admin as global_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory
from domains.parameters.admin import TopicOptionAdmin
from domains.parameters.forms import TopicOptionForm
from domains.parameters.models.topic_options import TopicOption


@pytest.mark.django_db
class TestTopicOptionAdmin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.site = AdminSite()
        self.admin = TopicOptionAdmin(TopicOption, self.site)
        self.factory = RequestFactory()

    def test_admin_registered(self):
        assert isinstance(self.admin, TopicOptionAdmin)
        assert global_admin.site.is_registered(TopicOption)

    def test_admin_form(self):
        assert self.admin.form == TopicOptionForm

    def test_admin_list_display(self):
        expected = ('description', 'is_active', 'created_at', 'updated_at')
        assert self.admin.list_display == expected

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

    def test_admin_search_returns_matching(self):
        topic_option = TopicOption.objects.create(description='Orçamento Anual')
        TopicOption.objects.create(description='Prestação de Contas')
        request = self.factory.get('/admin/parameters/topicoption/', {'q': 'anual'})
        request.user = User.objects.create_superuser('admin')
        queryset = self.admin.get_search_results(
            request, TopicOption.objects.all(), 'anual'
        )[0]
        assert set(queryset) == {topic_option}

    def test_admin_filter_by_active(self):
        active = TopicOption.objects.create(description='Opção Ativa')
        TopicOption.objects.create(description='Opção Inativa', is_active=False)
        request = self.factory.get('/admin/parameters/topicoption/', {'is_active__exact': '1'})
        request.user = User.objects.create_superuser('admin')
        queryset = self.admin.get_queryset(request).filter(is_active=True)
        assert set(queryset) == {active}

    def test_admin_has_change_form_permission(self):
        request = self.factory.get('/admin/parameters/topicoption/')
        request.user = User.objects.create_superuser('admin')
        assert self.admin.has_change_permission(request) is True

    def test_admin_has_add_permission(self):
        request = self.factory.get('/admin/parameters/topicoption/add/')
        request.user = User.objects.create_superuser('admin')
        assert self.admin.has_add_permission(request) is True

    def test_admin_has_delete_permission(self):
        request = self.factory.get('/admin/parameters/topicoption/1/delete/')
        request.user = User.objects.create_superuser('admin')
        assert self.admin.has_delete_permission(request) is True