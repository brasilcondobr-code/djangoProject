from datetime import date

import pytest

from domains.gatehouse.exceptions import ServiceTransitionError
from domains.gatehouse.models import ServiceTransition, ServiceTransitionObject
from domains.gatehouse.services import ServiceTransitionService

pytestmark = pytest.mark.django_db


class TestServiceTransitionServiceCreate:

    def _data(self, condominium, collaborator_out, collaborator_in):
        return {
            "condominium": condominium,
            "collaboratorEnd": collaborator_out,
            "collaboratorStart": collaborator_in,
            "releaseDate": date(2026, 9, 24),
            "observations": "  Passagem noturna  ",
        }

    def _object_data(self, category, **overrides):
        data = {
            "categoryObj": category,
            "itemObj": "  Portao  ",
            "amountObj": 2,
            "shiftDate": date(2026, 9, 24),
        }
        data.update(overrides)
        return data

    def test_create_transition(self, admin_user, condominium, collaborator_out, collaborator_in):
        transition = ServiceTransitionService.create_service_transition(
            self._data(condominium, collaborator_out, collaborator_in),
            user=admin_user,
        )
        assert transition.pk is not None
        assert transition.observations == "Passagem noturna"
        assert transition.is_active is True
        assert transition.created_by == admin_user

    def test_create_with_objects(self, admin_user, condominium, collaborator_out, collaborator_in, category):
        transition = ServiceTransitionService.create_service_transition(
            self._data(condominium, collaborator_out, collaborator_in),
            objects_data=[self._object_data(category)],
            user=admin_user,
        )
        assert transition.items.count() == 1
        item = transition.items.first()
        assert item.itemObj == "Portao"
        assert item.amountObj == 2
        assert item.shiftDate == date(2026, 9, 24)

    def test_create_duplicate_rejected(self, admin_user, condominium, collaborator_out, collaborator_in):
        ServiceTransitionService.create_service_transition(
            self._data(condominium, collaborator_out, collaborator_in)
        )
        with pytest.raises(ServiceTransitionError, match="Já existe"):
            ServiceTransitionService.create_service_transition(
                self._data(condominium, collaborator_out, collaborator_in)
            )

    @pytest.mark.parametrize("missing_field", ["condominium", "collaboratorEnd", "collaboratorStart", "releaseDate"])
    def test_create_missing_required_field(self, missing_field, condominium, collaborator_out, collaborator_in):
        data = self._data(condominium, collaborator_out, collaborator_in)
        data[missing_field] = None
        with pytest.raises(ServiceTransitionError, match="obrigatórios ausentes"):
            ServiceTransitionService.create_service_transition(data)

    def test_create_invalid_condominium(self, collaborator_out, collaborator_in):
        data = {
            "condominium": 999999,
            "collaboratorEnd": collaborator_out,
            "collaboratorStart": collaborator_in,
            "releaseDate": date(2026, 9, 24),
        }
        with pytest.raises(ServiceTransitionError, match="Condomínio não encontrado"):
            ServiceTransitionService.create_service_transition(data)

    def test_create_invalid_collaborator(self, condominium, collaborator_in):
        data = {
            "condominium": condominium,
            "collaboratorEnd": 999999,
            "collaboratorStart": collaborator_in,
            "releaseDate": date(2026, 9, 24),
        }
        with pytest.raises(ServiceTransitionError, match="Colaborador de saída não encontrado"):
            ServiceTransitionService.create_service_transition(data)

    def test_create_with_invalid_object_rolls_back(
        self, admin_user, condominium, collaborator_out, collaborator_in, category
    ):
        with pytest.raises(ServiceTransitionError):
            ServiceTransitionService.create_service_transition(
                self._data(condominium, collaborator_out, collaborator_in),
                objects_data=[
                    self._object_data(category),
                    self._object_data(category, amountObj=0),
                ],
                user=admin_user,
            )
        assert ServiceTransition.objects.count() == 0
        assert ServiceTransitionObject.objects.count() == 0


class TestServiceTransitionServiceObject:

    def _transition(self, condominium, collaborator_out, collaborator_in):
        return ServiceTransition.objects.create(
            condominium=condominium,
            collaboratorEnd=collaborator_out,
            collaboratorStart=collaborator_in,
            releaseDate=date(2026, 9, 24),
        )

    def _object_data(self, category, **overrides):
        data = {
            "categoryObj": category,
            "itemObj": "Cadeira",
            "amountObj": 1,
            "shiftDate": date(2026, 9, 24),
        }
        data.update(overrides)
        return data

    def test_add_object(self, transition, category):
        obj = ServiceTransitionService.add_object(
            transition, self._object_data(category, itemObj="  Cadeira  ")
        )
        assert obj.pk is not None
        assert obj.itemObj == "Cadeira"
        assert obj.service_transition == transition

    @pytest.mark.parametrize("amount", [0, -1, 1.5, "dois"])
    def test_add_object_invalid_amount(self, transition, category, amount):
        with pytest.raises(ServiceTransitionError, match="quantidade"):
            ServiceTransitionService.add_object(transition, self._object_data(category, amountObj=amount))

    def test_add_object_empty_item(self, transition, category):
        with pytest.raises(ServiceTransitionError, match="item"):
            ServiceTransitionService.add_object(transition, self._object_data(category, itemObj="   "))

    def test_add_object_missing_category(self, transition, category):
        with pytest.raises(ServiceTransitionError, match="categoria"):
            ServiceTransitionService.add_object(transition, self._object_data(category, categoryObj=None))

    def test_add_object_invalid_category(self, transition, category):
        with pytest.raises(ServiceTransitionError, match="Categoria não encontrada"):
            ServiceTransitionService.add_object(transition, self._object_data(category, categoryObj=999999))

    def test_add_object_invalid_transition(self, category):
        with pytest.raises(ServiceTransitionError, match="inválida"):
            ServiceTransitionService.add_object(None, self._object_data(category))

    def test_remove_object(self, transition, category):
        obj = ServiceTransitionService.add_object(transition, self._object_data(category))
        ServiceTransitionService.remove_object(transition, obj.pk)
        assert ServiceTransitionObject.objects.count() == 0

    def test_remove_object_not_found(self, transition, category):
        obj = ServiceTransitionService.add_object(transition, self._object_data(category))
        with pytest.raises(ServiceTransitionError, match="não encontrado"):
            ServiceTransitionService.remove_object(transition, obj.pk + 999)


class TestServiceTransitionServiceUpdateDelete:

    def test_update_observations(self, transition):
        updated = ServiceTransitionService.update_service_transition(
            transition, {"observations": "  Observação nova  "}
        )
        updated.refresh_from_db()
        assert updated.observations == "Observação nova"

    def test_update_is_active(self, transition):
        updated = ServiceTransitionService.update_service_transition(transition, {"is_active": False})
        updated.refresh_from_db()
        assert updated.is_active is False

    def test_update_relations_and_unique(self, transition, collaborator_out, collaborator_in):
        updated = ServiceTransitionService.update_service_transition(
            transition, {"releaseDate": date(2026, 9, 30)}
        )
        updated.refresh_from_db()
        assert updated.releaseDate == date(2026, 9, 30)

    def test_update_to_duplicate_rejected(self, transition, collaborator_out, collaborator_in):
        ServiceTransition.objects.create(
            condominium=transition.condominium,
            collaboratorEnd=collaborator_out,
            collaboratorStart=collaborator_in,
            releaseDate=date(2026, 10, 1),
        )
        with pytest.raises(ServiceTransitionError, match="Já existe"):
            ServiceTransitionService.update_service_transition(
                transition, {"releaseDate": date(2026, 10, 1)}
            )

    def test_update_invalid_transition(self):
        with pytest.raises(ServiceTransitionError, match="inválida"):
            ServiceTransitionService.update_service_transition(None, {"observations": "x"})

    def test_delete_transition_removes_objects(self, transition, category):
        ServiceTransitionService.add_object(
            transition,
            {
                "categoryObj": category,
                "itemObj": "Mesa",
                "amountObj": 1,
                "shiftDate": date(2026, 9, 24),
            },
        )
        ServiceTransitionService.delete_service_transition(transition)
        assert ServiceTransition.objects.count() == 0
        assert ServiceTransitionObject.objects.count() == 0

    def test_delete_invalid_transition(self):
        with pytest.raises(ServiceTransitionError, match="inválida"):
            ServiceTransitionService.delete_service_transition(None)


class TestServiceTransitionServiceQueries:

    def test_get_by_id(self, transition):
        fetched = ServiceTransitionService.get_service_transition_by_id(transition.pk)
        assert fetched.pk == transition.pk
        assert fetched.condominium == transition.condominium

    def test_get_by_id_not_found(self):
        with pytest.raises(ServiceTransitionError, match="não encontrada"):
            ServiceTransitionService.get_service_transition_by_id(999999)

    def test_get_all(self, transition):
        result = ServiceTransitionService.get_all_service_transitions()
        assert list(result) == [transition]
        assert any(lookup.startswith("items") for lookup in result._prefetch_related_lookups)

    def test_get_all_empty(self):
        assert list(ServiceTransitionService.get_all_service_transitions()) == []


class TestServiceTransitionServiceValidators:

    @pytest.mark.parametrize(
        "object_data, expected_message",
        [
            ({}, "obrigatórios"),
            ({"itemObj": "  ", "shiftDate": date(2026, 9, 24), "amountObj": 1, "categoryObj": 1}, "item"),
            ({"itemObj": "X", "amountObj": 1, "categoryObj": 1}, "data do turno"),
            ({"itemObj": "X", "shiftDate": date(2026, 9, 24), "amountObj": 1}, "categoria"),
        ],
    )
    def test_validate_object_data(self, object_data, expected_message):
        with pytest.raises(ServiceTransitionError, match=expected_message):
            ServiceTransitionService.validate_object_data(object_data)

    def test_validate_object_data_valid(self):
        assert ServiceTransitionService.validate_object_data(
            {
                "categoryObj": 1,
                "itemObj": "X",
                "amountObj": 1,
                "shiftDate": date(2026, 9, 24),
            }
        ) is True
