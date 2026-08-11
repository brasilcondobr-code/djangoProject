import pytest
from django.test import Client

from domains.administrative.forms import VirtualMeetingForm
from domains.administrative.services.virtual_meeting_participant_service import (
    VirtualMeetingParticipantService,
)
from domains.condominium.models import Condominium
from domains.parameters.models import Addresses, ResidentType, States, TypesCondominium
from domains.residents.models.condominium_unit import CondominiumUnit
from domains.residents.models.resident import Resident


@pytest.fixture
def _staff_user():
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='staff', password='12345', is_staff=True,
    )


@pytest.fixture
def _other_condo(_address, _type_condo):
    return Condominium.objects.create(
        code='COND002', name='Condomínio Dois',
        cnpj='22.333.444/0001-22', state_registration='111111111',
        municipal_registration='222222222',
        type_condominium=_type_condo, address=_address,
    )


@pytest.fixture
def _other_type():
    return ResidentType.objects.create(description='Inquilino')


@pytest.fixture
def _resident_other_type(_other_type, _condo_unit):
    return Resident.objects.create(
        unit=_condo_unit,
        type_of_resident=_other_type,
        name='Maria Oliveira',
        email='maria@example.com',
        phone='(11) 98888-0000',
        cpf='987.654.321-00',
        rg='98.765.432-1',
        sex='F',
        date_of_birth='1985-01-01',
    )


@pytest.mark.django_db
class TestParticipantsByGroupView:

    def test_requires_login(self):
        response = Client().get('/administrative/ajax/participants-by-group/')
        assert response.status_code in (301, 302)

    def test_requires_staff(self, _resident):
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='comum', password='12345')
        client = Client()
        client.force_login(user)
        response = client.get('/administrative/ajax/participants-by-group/')
        assert response.status_code in (301, 302)

    def test_returns_residents_of_group(self, _staff_user, _resident_type, _resident):
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {'group_ids': [_resident_type.pk]},
        )
        assert response.status_code == 200
        payload = response.json()
        results = payload['results']
        assert len(results) == 1
        assert results[0]['id'] == _resident.pk
        assert results[0]['text'] == str(_resident)

    def test_multiple_groups_union(self, _staff_user, _resident_type, _resident,
                                   _other_type, _resident_other_type):
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {'group_ids': [_resident_type.pk, _other_type.pk]},
        )
        assert response.status_code == 200
        ids = {r['id'] for r in response.json()['results']}
        assert ids == {_resident.pk, _resident_other_type.pk}

    def test_empty_results_without_groups(self, _staff_user):
        client = Client()
        client.force_login(_staff_user)
        response = client.get('/administrative/ajax/participants-by-group/')
        assert response.status_code == 200
        assert response.json() == {'results': []}

    def test_invalid_group_id(self, _staff_user):
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {'group_ids': ['abc']},
        )
        assert response.status_code == 400

    def test_nonexistent_group_id(self, _staff_user):
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {'group_ids': [999999]},
        )
        assert response.status_code == 400

    def test_invalid_condominium_id(self, _staff_user, _resident_type):
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {'group_ids': [_resident_type.pk], 'condominium_id': 999999},
        )
        assert response.status_code == 400

    def test_filters_by_condominium(self, _staff_user, _resident_type, _resident, _other_condo):
        other_unit = CondominiumUnit.objects.create(
            condominium=_other_condo, tower='C', unit_number='303', floor='3',
        )
        Resident.objects.create(
            unit=other_unit,
            type_of_resident=_resident_type,
            name='Carlos Souza',
            email='carlos@example.com',
            phone='(11) 97777-0000',
            cpf='111.222.333-44',
            rg='11.222.333-4',
            sex='M',
            date_of_birth='1975-01-01',
        )
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {
                'group_ids': [_resident_type.pk],
                'condominium_id': _other_condo.pk,
            },
        )
        assert response.status_code == 200
        ids = [r['id'] for r in response.json()['results']]
        assert _resident.pk not in ids
        assert len(ids) == 1

    def test_response_has_no_sensitive_data(self, _staff_user, _resident_type, _resident):
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {'group_ids': [_resident_type.pk]},
        )
        raw = response.content.decode()
        assert _resident.cpf not in raw
        assert _resident.email not in raw
        assert _resident.phone not in raw

    def test_only_active_residents_returned(self, _staff_user, _resident_type, _resident):
        _resident.is_active = False
        _resident.save()
        client = Client()
        client.force_login(_staff_user)
        response = client.get(
            '/administrative/ajax/participants-by-group/',
            {'group_ids': [_resident_type.pk]},
        )
        assert response.status_code == 200
        assert response.json()['results'] == []


@pytest.mark.django_db
class TestVirtualMeetingParticipantService:

    def test_empty_group_ids_returns_none(self, _resident):
        qs = VirtualMeetingParticipantService.get_residents_by_groups([])
        assert not qs.exists()

    def test_filters_by_groups(self, _resident_type, _resident, _other_type, _resident_other_type):
        qs = VirtualMeetingParticipantService.get_residents_by_groups([_resident_type.pk])
        assert list(qs) == [_resident]

    def test_filters_by_condominium(self, _resident_type, _resident, _other_condo):
        other_unit = CondominiumUnit.objects.create(
            condominium=_other_condo, tower='C', unit_number='303', floor='3',
        )
        other = Resident.objects.create(
            unit=other_unit,
            type_of_resident=_resident_type,
            name='Carlos Souza',
            email='carlos@example.com',
            phone='(11) 97777-0000',
            cpf='111.222.333-44',
            rg='11.222.333-4',
            sex='M',
            date_of_birth='1975-01-01',
        )
        qs = VirtualMeetingParticipantService.get_residents_by_groups(
            [_resident_type.pk], condominium=_other_condo,
        )
        assert list(qs) == [other]

    def test_distinct_residents_in_multiple_groups(
        self, _resident_type, _resident, _other_type,
    ):
        _resident.type_of_resident = _other_type
        _resident.save()
        qs = VirtualMeetingParticipantService.get_residents_by_groups(
            [_resident_type.pk, _other_type.pk],
        )
        assert list(qs) == [_resident]

    def test_invalid_participant_ids_detected(
        self, _resident_type, _resident, _other_type, _resident_other_type,
    ):
        invalid = VirtualMeetingParticipantService.get_invalid_participant_ids(
            participant_ids=[_resident.pk, _resident_other_type.pk],
            group_ids=[_resident_type.pk],
        )
        assert invalid == {_resident_other_type.pk}

    def test_valid_participant_ids_all_valid(self, _resident_type, _resident):
        invalid = VirtualMeetingParticipantService.get_invalid_participant_ids(
            participant_ids=[_resident.pk],
            group_ids=[_resident_type.pk],
        )
        assert invalid == set()


def _form_data(meeting, **overrides):
    data = {
        'condominium': meeting.condominium_id,
        'title': 'Assembleia Geral',
        'president': 'João',
        'secretary': 'Maria',
        'meeting_date_time_start': meeting.meeting_date_time_start,
        'meeting_date_time_end': meeting.meeting_date_time_end,
        'meeting_date_time_voting_begins': meeting.meeting_date_time_voting_begins,
        'meeting_date_time_voting_end': meeting.meeting_date_time_voting_end,
        'notice_meeting_date_time': meeting.notice_meeting_date_time,
        'notice_meeting_send_email_participants': False,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestVirtualMeetingParticipantsValidation:

    def test_valid_single_group_with_multiple_participants(
        self, _meeting, _resident_type, _resident,
    ):
        second = Resident.objects.create(
            unit=_resident.unit,
            type_of_resident=_resident_type,
            name='Ana Paula',
            email='ana@example.com',
            phone='(11) 96666-0000',
            cpf='222.333.444-55',
            rg='22.333.444-5',
            sex='F',
            date_of_birth='1980-01-01',
        )
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident.pk, second.pk],
        ))
        assert form.is_valid(), form.errors

    def test_participant_not_in_selected_group(
        self, _meeting, _resident_type, _resident, _other_type, _resident_other_type,
    ):
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
            participating_resident=[_resident_other_type.pk],
        ))
        assert not form.is_valid()
        assert 'não pertencem aos grupos selecionados' in form.errors['participating_resident'][0]

    def test_participants_without_groups(
        self, _meeting, _resident_type, _resident,
    ):
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups='',
            participating_resident=[_resident.pk],
        ))
        assert not form.is_valid()
        assert 'Selecione ao menos um grupo de participantes.' in form.errors['participating_resident']

    def test_participant_from_other_condominium(
        self, _meeting, _resident_type, _resident, _other_condo,
    ):
        other_unit = CondominiumUnit.objects.create(
            condominium=_other_condo, tower='C', unit_number='303', floor='3',
        )
        other_resident = Resident.objects.create(
            unit=other_unit,
            type_of_resident=_resident_type,
            name='Carlos Souza',
            email='carlos@example.com',
            phone='(11) 97777-0000',
            cpf='111.222.333-44',
            rg='11.222.333-4',
            sex='M',
            date_of_birth='1975-01-01',
        )
        form = VirtualMeetingForm(data=_form_data(
            _meeting,
            participating_groups=_resident_type.pk,
            participating_resident=[other_resident.pk],
        ))
        assert not form.is_valid()
        assert 'não pertencem aos grupos selecionados' in form.errors['participating_resident'][0]
