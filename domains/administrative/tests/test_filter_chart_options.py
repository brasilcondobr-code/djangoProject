import json
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from domains.parameters.models import (
    Chartofaccountstype, Accountingclasstypes,
    ChartofaccountsMaingroup, ChartofaccountsSubgroup,
)


@pytest.mark.django_db
class TestFilterClassesByType:

    @pytest.fixture
    def staff_user(self):
        return User.objects.create_user(username='staff', password='pass', is_staff=True)

    @pytest.fixture
    def acc_type(self):
        return Chartofaccountstype.objects.create(code='T001', description='Receita', nature='devedora')

    @pytest.fixture
    def acc_class(self, acc_type):
        return Accountingclasstypes.objects.create(
            code='C001', description='Entradas', account_type=acc_type, is_active=True,
        )

    def _login(self, client, user):
        client.force_login(user)

    def test_requires_staff(self, client):
        url = reverse('filter_classes_by_type')
        response = client.get(url, {'tipo_conta_id': 1})
        assert response.status_code == 302

    def test_returns_400_without_param(self, client, staff_user):
        self._login(client, staff_user)
        url = reverse('filter_classes_by_type')
        response = client.get(url)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data == {'results': []}

    def test_returns_400_with_invalid_param(self, client, staff_user):
        self._login(client, staff_user)
        url = reverse('filter_classes_by_type')
        response = client.get(url, {'tipo_conta_id': 'abc'})
        assert response.status_code == 400

    def test_returns_classes(self, client, staff_user, acc_type, acc_class):
        self._login(client, staff_user)
        url = reverse('filter_classes_by_type')
        response = client.get(url, {'tipo_conta_id': acc_type.pk})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data['results']) == 1
        assert data['results'][0]['id'] == acc_class.pk
        assert data['results'][0]['text'] == 'C001 - Entradas (Receita)'

    def test_returns_empty_when_no_classes(self, client, staff_user, acc_type):
        self._login(client, staff_user)
        url = reverse('filter_classes_by_type')
        response = client.get(url, {'tipo_conta_id': 9999})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['results'] == []


@pytest.mark.django_db
class TestFilterGroupsByClass:

    @pytest.fixture
    def staff_user(self):
        return User.objects.create_user(username='staff2', password='pass', is_staff=True)

    @pytest.fixture
    def acc_type(self):
        return Chartofaccountstype.objects.create(code='T002', description='Despesa', nature='devedora')

    @pytest.fixture
    def acc_class(self, acc_type):
        return Accountingclasstypes.objects.create(
            code='C002', description='Saídas', account_type=acc_type, is_active=True,
        )

    @pytest.fixture
    def group(self, acc_class):
        return ChartofaccountsMaingroup.objects.create(
            code='G001', description='Grupo Principal', account_class=acc_class, is_active=True,
        )

    def _login(self, client, user):
        client.force_login(user)

    def test_requires_staff(self, client):
        url = reverse('filter_groups_by_class')
        response = client.get(url, {'classe_contabil_id': 1})
        assert response.status_code == 302

    def test_returns_400_without_param(self, client, staff_user):
        self._login(client, staff_user)
        url = reverse('filter_groups_by_class')
        response = client.get(url)
        assert response.status_code == 400

    def test_returns_groups(self, client, staff_user, acc_class, group):
        self._login(client, staff_user)
        url = reverse('filter_groups_by_class')
        response = client.get(url, {'classe_contabil_id': acc_class.pk})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data['results']) == 1
        assert data['results'][0]['id'] == group.pk
        assert 'G001' in data['results'][0]['text']
        assert 'Grupo Principal' in data['results'][0]['text']
        assert 'Saídas' in data['results'][0]['text']


@pytest.mark.django_db
class TestFilterSubgroupsByGroup:

    @pytest.fixture
    def staff_user(self):
        return User.objects.create_user(username='staff3', password='pass', is_staff=True)

    @pytest.fixture
    def acc_type(self):
        return Chartofaccountstype.objects.create(code='T003', description='Ativo', nature='devedora')

    @pytest.fixture
    def acc_class(self, acc_type):
        return Accountingclasstypes.objects.create(
            code='C003', description='Circulante', account_type=acc_type, is_active=True,
        )

    @pytest.fixture
    def group(self, acc_class):
        return ChartofaccountsMaingroup.objects.create(
            code='G002', description='Outro Grupo', account_class=acc_class, is_active=True,
        )

    @pytest.fixture
    def subgroup(self, group):
        return ChartofaccountsSubgroup.objects.create(
            code='S001', description='Sub Grupo Teste', main_group=group, is_active=True,
        )

    def _login(self, client, user):
        client.force_login(user)

    def test_requires_staff(self, client):
        url = reverse('filter_subgroups_by_group')
        response = client.get(url, {'grupo_principal_id': 1})
        assert response.status_code == 302

    def test_returns_400_without_param(self, client, staff_user):
        self._login(client, staff_user)
        url = reverse('filter_subgroups_by_group')
        response = client.get(url)
        assert response.status_code == 400

    def test_returns_subgroups(self, client, staff_user, group, subgroup):
        self._login(client, staff_user)
        url = reverse('filter_subgroups_by_group')
        response = client.get(url, {'grupo_principal_id': group.pk})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data['results']) == 1
        assert data['results'][0]['id'] == subgroup.pk
        assert 'S001' in data['results'][0]['text']
        assert 'Sub Grupo Teste' in data['results'][0]['text']
        assert 'Outro Grupo' in data['results'][0]['text']
