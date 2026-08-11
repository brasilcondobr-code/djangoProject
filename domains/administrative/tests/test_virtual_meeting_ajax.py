import pytest
from django.test import Client
from django.contrib.auth.models import User


@pytest.fixture
def _staff_user():
    user = User.objects.create_user(username='admin', password='12345', is_staff=True)
    return user


@pytest.mark.django_db
class TestGetResidentsByTypeView:

    def test_requires_login(self):
        response = Client().get('/administrative/ajax/residents-by-type/', {'type_id': 1})
        assert response.status_code in (301, 302)

    def test_returns_residents(self, _staff_user, _resident_type, _resident, _condo_unit, _condo):
        from domains.residents.models.resident import Resident
        from domains.residents.models.condominium_unit import CondominiumUnit
        other_unit = CondominiumUnit.objects.create(
            condominium=_condo, tower='B', unit_number='202', floor='2',
        )
        Resident.objects.create(
            unit=other_unit,
            type_of_resident=_resident_type,
            name='Maria Oliveira',
            email='maria@example.com',
            phone='(11) 98888-0000',
            cpf='987.654.321-00',
            rg='98.765.432-1',
            sex='F',
            date_of_birth='1985-01-01',
        )

        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/residents-by-type/',
            {'type_id': _resident_type.pk},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload['success'] is True
        names = [r['name'] for r in payload['residents']]
        assert len(names) == 2

    def test_missing_type(self, _staff_user):
        client = Client()
        client.force_login(_staff_user)
        response = client.get('/administrative/ajax/residents-by-type/')
        assert response.status_code == 400
        assert response.json()['success'] is False