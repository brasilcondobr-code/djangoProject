from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from domains.gatehouse.models import ServiceTransition, ServiceTransitionObject

pytestmark = pytest.mark.django_db


class TestServiceTransitionModel:

    def _make_transition(self, condominium, collaborator_out, collaborator_in):
        return ServiceTransition.objects.create(
            condominium=condominium,
            collaboratorEnd=collaborator_out,
            collaboratorStart=collaborator_in,
            releaseDate=date(2026, 9, 24),
            observations="Turno noturno conferido",
        )

    def test_fields_exist(self, condominium, collaborator_out, collaborator_in):
        transition = self._make_transition(condominium, collaborator_out, collaborator_in)
        assert transition.condominium == condominium
        assert transition.collaboratorEnd == collaborator_out
        assert transition.collaboratorStart == collaborator_in
        assert transition.releaseDate == date(2026, 9, 24)
        assert transition.observations == "Turno noturno conferido"

    def test_default_is_active_true(self, condominium, collaborator_out, collaborator_in):
        transition = self._make_transition(condominium, collaborator_out, collaborator_in)
        assert transition.is_active is True

    def test_str_format(self, condominium, collaborator_out, collaborator_in):
        transition = self._make_transition(condominium, collaborator_out, collaborator_in)
        assert str(transition) == "02. Passagem de Serviço %s" % transition.pk

    def test_observations_is_optional(self, condominium, collaborator_out, collaborator_in):
        transition = ServiceTransition.objects.create(
            condominium=condominium,
            collaboratorEnd=collaborator_out,
            collaboratorStart=collaborator_in,
            releaseDate=date(2026, 9, 24),
        )
        assert transition.observations is None

    def test_unique_constraint_blocks_duplicates(self, condominium, collaborator_out, collaborator_in):
        self._make_transition(condominium, collaborator_out, collaborator_in)
        with pytest.raises(IntegrityError), transaction.atomic():
            self._make_transition(condominium, collaborator_out, collaborator_in)

    def test_unique_constraint_allows_different_date(self, condominium, collaborator_out, collaborator_in):
        first = self._make_transition(condominium, collaborator_out, collaborator_in)
        second = ServiceTransition.objects.create(
            condominium=condominium,
            collaboratorEnd=collaborator_out,
            collaboratorStart=collaborator_in,
            releaseDate=date(2026, 9, 25),
        )
        assert first.pk != second.pk

    def test_related_names(self, condominium, collaborator_out, collaborator_in):
        transition = self._make_transition(condominium, collaborator_out, collaborator_in)
        assert list(condominium.service_transitions.all()) == [transition]
        assert list(collaborator_out.service_transitions_end.all()) == [transition]
        assert list(collaborator_in.service_transitions_start.all()) == [transition]

    def test_ordering_meta(self):
        assert ServiceTransition._meta.ordering == ["-releaseDate", "-id"]

    def test_cascade_delete_removes_objects(self, condominium, collaborator_out, collaborator_in, category):
        transition = self._make_transition(condominium, collaborator_out, collaborator_in)
        ServiceTransitionObject.objects.create(
            service_transition=transition,
            categoryObj=category,
            itemObj="Monitor",
            amountObj=2,
            shiftDate=date(2026, 9, 24),
        )
        transition.delete()
        assert ServiceTransitionObject.objects.count() == 0


class TestServiceTransitionObjectModel:

    def _make_object(self, transition, category, **overrides):
        data = {
            "service_transition": transition,
            "categoryObj": category,
            "itemObj": "Cadeira",
            "amountObj": 1,
            "shiftDate": date(2026, 9, 24),
        }
        data.update(overrides)
        return ServiceTransitionObject.objects.create(**data)

    def test_fields_exist(self, transition, category):
        obj = self._make_object(transition, category)
        assert obj.service_transition == transition
        assert obj.categoryObj == category
        assert obj.itemObj == "Cadeira"
        assert obj.amountObj == 1
        assert obj.shiftDate == date(2026, 9, 24)

    def test_default_amount_is_one(self, transition, category):
        obj = self._make_object(transition, category, amountObj=1)
        assert obj.amountObj == 1

    def test_amount_zero_rejected_by_validator(self, transition, category):
        obj = self._make_object(transition, category, amountObj=1)
        obj.amountObj = 0
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_description_field_removed(self):
        from django.core.exceptions import FieldDoesNotExist

        with pytest.raises(FieldDoesNotExist):
            ServiceTransitionObject._meta.get_field("description")

    def test_time_fields_removed(self):
        from django.core.exceptions import FieldDoesNotExist

        for field_name in ("startTime", "endTime"):
            with pytest.raises(FieldDoesNotExist):
                ServiceTransitionObject._meta.get_field(field_name)

    def test_shift_date_defaults_to_today(self, transition, category):
        from django.utils import timezone

        obj = ServiceTransitionObject.objects.create(
            service_transition=transition,
            categoryObj=category,
            itemObj="Mesa",
            amountObj=1,
        )
        assert obj.shiftDate == timezone.localdate()

    def test_str_format(self, transition, category):
        obj = self._make_object(transition, category)
        assert str(obj) == "Cadeira (1)"

    def test_related_name_items(self, transition, category):
        obj = self._make_object(transition, category)
        assert list(transition.items.all()) == [obj]

    def test_ordering_meta(self):
        assert ServiceTransitionObject._meta.ordering == ["shiftDate", "id"]

    def test_category_fk_points_to_concierge_service_category(self):
        from django.db import models
        from domains.parameters.models import ConciergeServiceCategory

        field = ServiceTransitionObject._meta.get_field("categoryObj")
        assert field.related_model is ConciergeServiceCategory
        assert field.remote_field.get_accessor_name() == "parameters"
        assert field.remote_field.on_delete is models.CASCADE
