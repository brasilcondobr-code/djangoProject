import pytest
from django.db import IntegrityError

from domains.parameters.models.types_of_maintenance_reservations import (
    TypesOfMaintenanceReservations,
)


@pytest.mark.django_db
class TestTypesOfMaintenanceReservationsModel:

    def test_create_valid(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Preventiva'
        )
        assert maintenance.pk is not None
        assert maintenance.description == 'Manutenção Preventiva'

    def test_default_is_active_true(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Corretiva'
        )
        assert maintenance.is_active is True

    def test_created_at_auto_set(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção de Elevadores'
        )
        assert maintenance.created_at is not None

    def test_updated_at_changes_on_update(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Hidráulica'
        )
        original_updated = maintenance.updated_at
        maintenance.description = 'Manutenção Hidráulica Preventiva'
        maintenance.save()
        maintenance.refresh_from_db()
        assert maintenance.updated_at >= original_updated

    def test_str_returns_description(self):
        maintenance = TypesOfMaintenanceReservations.objects.create(
            description='Manutenção Elétrica'
        )
        assert str(maintenance) == 'Manutenção Elétrica'

    def test_duplicate_description_raises(self):
        TypesOfMaintenanceReservations.objects.create(
            description='Manutenção de Piscina'
        )
        with pytest.raises(IntegrityError):
            TypesOfMaintenanceReservations.objects.create(
                description='Manutenção de Piscina'
            )

    def test_description_required(self):
        with pytest.raises(IntegrityError):
            TypesOfMaintenanceReservations.objects.create(description=None)

    def test_description_max_length(self):
        field = TypesOfMaintenanceReservations._meta.get_field('description')
        assert field.max_length == 255

    def test_description_null_blank_false(self):
        field = TypesOfMaintenanceReservations._meta.get_field('description')
        assert field.null is False
        assert field.blank is False

    def test_description_unique_flag(self):
        field = TypesOfMaintenanceReservations._meta.get_field('description')
        assert field.unique is True

    def test_no_redundant_unique_together(self):
        assert TypesOfMaintenanceReservations._meta.unique_together == ()

    def test_no_redundant_unique_constraint(self):
        names = [constraint.name for constraint in TypesOfMaintenanceReservations._meta.constraints]
        assert names == []

    def test_verbose_names(self):
        assert (
            TypesOfMaintenanceReservations._meta.verbose_name
            == '28. Tipo de Manutenção'
        )
        assert (
            TypesOfMaintenanceReservations._meta.verbose_name_plural
            == '28. Tipos de Manutenções'
        )

    def test_app_label(self):
        assert TypesOfMaintenanceReservations._meta.app_label == 'parameters'

    def test_db_table(self):
        assert (
            TypesOfMaintenanceReservations._meta.db_table
            == 'parameters_typesofmaintenancereservations'
        )

    def test_ordering(self):
        assert TypesOfMaintenanceReservations._meta.ordering == ['description']

    def test_ordering_applied(self):
        first = TypesOfMaintenanceReservations.objects.create(description='Aaa')
        second = TypesOfMaintenanceReservations.objects.create(description='Bbb')
        assert list(TypesOfMaintenanceReservations.objects.all()) == [first, second]
